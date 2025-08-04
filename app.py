import streamlit as st
import os
import traceback
from advisor_agent import AdvisorAgent

# Configure the page
st.set_page_config(
    page_title="Financial Planning Agent - Valura.ai",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem 0;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
}
.user-message {
    background-color: #e3f2fd;
    margin-left: 20%;
}
.bot-message {
    background-color: #f5f5f5;
    margin-right: 20%;
}
.summary-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'questionnaire_complete' not in st.session_state:
        st.session_state.questionnaire_complete = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'waiting_for_answer' not in st.session_state:
        st.session_state.waiting_for_answer = False

def main():
    initialize_session_state()

    st.markdown("""
    <div class="main-header">
        <h1>💰 Financial Planning Agent</h1>
        <p>Your AI-powered retirement planning advisor by Valura.ai</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔧 Local Setup")
        if not st.session_state.agent:
            try:
                st.session_state.agent = AdvisorAgent(openai_api_key=None)
                if not st.session_state.questionnaire_complete:
                    question, is_complete = st.session_state.agent.ask_next_question()
                    st.session_state.current_question = question
                    st.session_state.waiting_for_answer = not is_complete
                    st.session_state.questionnaire_complete = is_complete
            except Exception as e:
                # Show the full error with traceback
                st.error(f"Failed to initialize agent:")
                st.error(f"Error: {str(e)}")
                st.error("Full traceback:")
                st.code(traceback.format_exc())

        if st.session_state.agent and st.session_state.questionnaire_complete:
            st.header("📊 Quick Actions")
            if st.button("📈 Retirement Forecast"):
                response = st.session_state.agent.chat("Show me my retirement forecast")
                st.session_state.chat_history.append(("You", "Show me my retirement forecast"))
                st.session_state.chat_history.append(("Advisor", response))
                st.rerun()

            if st.button("💰 Savings Analysis"):
                response = st.session_state.agent.chat("Analyze my current savings plan")
                st.session_state.chat_history.append(("You", "Analyze my current savings plan"))
                st.session_state.chat_history.append(("Advisor", response))
                st.rerun()

    if not st.session_state.agent:
        st.info("Initializing your financial advisor...")
        return

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("💬 Chat with Your Advisor")

        with st.container():
            if not st.session_state.questionnaire_complete and st.session_state.current_question:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 Advisor:</strong><br>
                    {st.session_state.current_question}
                </div>
                """, unsafe_allow_html=True)

            for sender, message in st.session_state.chat_history:
                class_name = "user-message" if sender == "You" else "bot-message"
                icon = "👤 You" if sender == "You" else "🤖 Advisor"
                st.markdown(f"""
                <div class="chat-message {class_name}">
                    <strong>{icon}:</strong><br>
                    {message}
                </div>
                """, unsafe_allow_html=True)

        user_input = st.text_input("Your message:", key="user_input", placeholder="Ask me anything about retirement planning...")

        if st.button("Send") and user_input:
            st.session_state.chat_history.append(("You", user_input))

            if st.session_state.waiting_for_answer:
                feedback = st.session_state.agent.process_answer(user_input)
                st.session_state.chat_history.append(("Advisor", feedback))

                question, is_complete = st.session_state.agent.ask_next_question()
                if not is_complete:
                    st.session_state.current_question = question
                    st.session_state.chat_history.append(("Advisor", question))
                else:
                    st.session_state.questionnaire_complete = True
                    st.session_state.waiting_for_answer = False
                    st.session_state.chat_history.append(("Advisor", question))
            else:
                response = st.session_state.agent.chat(user_input)
                st.session_state.chat_history.append(("Advisor", response))

            st.rerun()

    with col2:
        st.header("📊 Your Profile")

        if st.session_state.agent and st.session_state.questionnaire_complete:
            profile = st.session_state.agent.profile

            st.markdown(f"""
            <div class="summary-card">
                <h3>💼 Financial Summary</h3>
                <p><strong>Age:</strong> {profile.age}</p>
                <p><strong>Income:</strong> ${profile.income:,.0f}/year</p>
                <p><strong>Savings:</strong> ${profile.current_savings:,.0f}</p>
                <p><strong>Monthly Savings:</strong> ${profile.monthly_savings:,.0f}</p>
                <p><strong>Target Retirement:</strong> Age {profile.retirement_age}</p>
                <p><strong>Expected Return:</strong> {profile.expected_return*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

            years_to_retirement = profile.retirement_age - profile.age
            if years_to_retirement > 0:
                st.metric("Years to Retirement", years_to_retirement)
                if profile.expected_return > 0:
                    doubling_time = 72 / (profile.expected_return * 100)
                    st.metric("Investment Doubling Time", f"{doubling_time:.1f} years")
        else:
            st.info("Complete the questionnaire to see your financial profile.")

        st.header("💡 Try These Questions")
        sample_questions = [
            "When can I retire?",
            "How much should I save monthly?",
            "What if inflation is 4%?",
            "How long will $500k last in retirement?",
            "Should I pay off my mortgage early?",
            "What's the rule of 72?",
            "Explain the calculations you used"
        ]

        for question in sample_questions:
            if st.button(question, key=f"sample_{question}"):
                st.session_state.chat_history.append(("You", question))
                if st.session_state.questionnaire_complete:
                    response = st.session_state.agent.chat(question)
                    st.session_state.chat_history.append(("Advisor", response))
                else:
                    st.session_state.chat_history.append(("Advisor", "Please complete the questionnaire first!"))
                st.rerun()

if __name__ == "__main__":
    main()