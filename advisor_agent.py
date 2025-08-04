from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import formulas


class UserProfile:
    def __init__(self):
        self.age = None
        self.income = None
        self.current_savings = None
        self.monthly_savings = None
        self.retirement_age = None
        self.expected_return = 0.07  # 7% default
        self.inflation_rate = 0.03
        self.risk_tolerance = "moderate"
        self.retirement_goal = None
        self.is_complete = False

    def to_dict(self):
        return {
            'age': self.age,
            'income': self.income,
            'current_savings': self.current_savings,
            'monthly_savings': self.monthly_savings,
            'retirement_age': self.retirement_age,
            'expected_return': self.expected_return,
            'inflation_rate': self.inflation_rate,
            'risk_tolerance': self.risk_tolerance,
            'retirement_goal': self.retirement_goal
        }


class AdvisorAgent:
    def __init__(self, openai_api_key: str):
        self.profile = UserProfile()
        self.question_index = 0
        self.questions = [
            "What's your current age?",
            "What's your annual income (in dollars)?",
            "How much have you saved so far (in dollars)?",
            "How much do you save each month (in dollars)?",
            "At what age would you like to retire?",
            "What's your risk tolerance? (conservative/moderate/aggressive)",
            "How much annual income do you want in retirement (in dollars)?"
        ]

        # Initialize the LLM without complex agent setup for now
        try:
            self.llm = ChatOllama(model="mistral")
        except Exception as e:
            print(f"Error initializing ChatOllama: {e}")
            raise

    def _calculate_with_tools(self, calculation_type: str, **kwargs):
        """Handle financial calculations directly"""
        try:
            if calculation_type == "future_value":
                return formulas.future_value(kwargs['pv'], kwargs['rate'], kwargs['n'])
            elif calculation_type == "present_value":
                return formulas.present_value(kwargs['fv'], kwargs['rate'], kwargs['n'])
            elif calculation_type == "retirement_age":
                return formulas.calculate_retirement_age(
                    kwargs['current_age'], kwargs['current_savings'],
                    kwargs['monthly_savings'], kwargs['target_amount'],
                    kwargs['annual_return']
                )
            elif calculation_type == "savings_longevity":
                return formulas.calculate_savings_longevity(
                    kwargs['initial_amount'], kwargs['monthly_withdrawal'],
                    kwargs['annual_return']
                )
            elif calculation_type == "monthly_savings_needed":
                return formulas.monthly_savings_needed(
                    kwargs['target_amount'], kwargs['years'], kwargs['annual_return']
                )
            elif calculation_type == "rule_of_72":
                return formulas.rule_of_72(kwargs['rate_percent'])
            else:
                return None
        except Exception as e:
            return f"Calculation error: {str(e)}"

    def ask_next_question(self) -> tuple[str, bool]:
        if self.question_index >= len(self.questions):
            self.profile.is_complete = True
            return self._generate_summary(), True
        question = self.questions[self.question_index]
        return f"📝 Question {self.question_index + 1}/{len(self.questions)}: {question}", False

    def process_answer(self, answer: str) -> str:
        try:
            if self.question_index == 0:
                self.profile.age = int(answer)
            elif self.question_index == 1:
                self.profile.income = float(answer.replace('$', '').replace(',', ''))
            elif self.question_index == 2:
                self.profile.current_savings = float(answer.replace('$', '').replace(',', ''))
            elif self.question_index == 3:
                self.profile.monthly_savings = float(answer.replace('$', '').replace(',', ''))
            elif self.question_index == 4:
                self.profile.retirement_age = int(answer)
            elif self.question_index == 5:
                risk = answer.lower()
                if 'conservative' in risk:
                    self.profile.risk_tolerance = 'conservative'
                    self.profile.expected_return = 0.05
                elif 'aggressive' in risk:
                    self.profile.risk_tolerance = 'aggressive'
                    self.profile.expected_return = 0.09
                else:
                    self.profile.risk_tolerance = 'moderate'
                    self.profile.expected_return = 0.07
            elif self.question_index == 6:
                self.profile.retirement_goal = float(answer.replace('$', '').replace(',', ''))

            self.question_index += 1
            return "Got it! ✅"
        except ValueError:
            return "❌ Please enter a valid number."

    def _generate_summary(self) -> str:
        years_to_retirement = self.profile.retirement_age - self.profile.age
        months_to_retirement = years_to_retirement * 12
        monthly_rate = self.profile.expected_return / 12

        future_current = formulas.future_value(self.profile.current_savings, monthly_rate, months_to_retirement)
        future_monthly = formulas.fv_annuity(self.profile.monthly_savings, monthly_rate, months_to_retirement)
        total_at_retirement = future_current + future_monthly

        retirement_rate = 0.04
        needed_amount = self.profile.retirement_goal / retirement_rate
        surplus_deficit = total_at_retirement - needed_amount

        summary = f"""
**Your Retirement Plan Summary**

**Current Situation:**
- Age: {self.profile.age}
- Years to retirement: {years_to_retirement}
- Current savings: ${self.profile.current_savings:,.2f}
- Monthly savings: ${self.profile.monthly_savings:,.2f}
- Expected return: {self.profile.expected_return*100:.1f}%

**Projected Results:**
- Total at retirement: ${total_at_retirement:,.2f}
- Amount needed for ${self.profile.retirement_goal:,.2f}/year: ${needed_amount:,.2f}
- Surplus/Deficit: ${surplus_deficit:,.2f}

**Status:** {"✅ On track!" if surplus_deficit >= 0 else "⚠️ Need to save more"}

You can now ask me questions like:
- "When can I retire if I save more?"
- "How long will my money last in retirement?"
- "What if inflation is higher?"
        """
        return summary

    def chat(self, message: str) -> str:
        """Simple chat function that handles common financial questions"""
        try:
            if not self.profile.is_complete:
                return "Please complete the questionnaire first!"

            message_lower = message.lower()
            
            # Handle specific financial calculations
            if "when can i retire" in message_lower:
                result = self._calculate_with_tools("retirement_age",
                    current_age=self.profile.age,
                    current_savings=self.profile.current_savings,
                    monthly_savings=self.profile.monthly_savings,
                    target_amount=self.profile.retirement_goal / 0.04,
                    annual_return=self.profile.expected_return
                )
                if result:
                    return f"Based on your current savings plan, you can retire at age {result:.1f}"
                else:
                    return "You may need to save more or adjust your retirement goals to reach your target."
            
            elif "how long will" in message_lower and ("last" in message_lower or "money" in message_lower):
                # Assume 4% withdrawal rule
                annual_withdrawal = self.profile.retirement_goal
                monthly_withdrawal = annual_withdrawal / 12
                retirement_savings = self.profile.retirement_goal / 0.04
                
                result = self._calculate_with_tools("savings_longevity",
                    initial_amount=retirement_savings,
                    monthly_withdrawal=monthly_withdrawal,
                    annual_return=self.profile.expected_return
                )
                
                if result == float('inf'):
                    return "Your savings should last indefinitely with proper management!"
                else:
                    return f"Your savings would last approximately {result:.1f} years in retirement."
            
            elif "rule of 72" in message_lower:
                rate_percent = self.profile.expected_return * 100
                result = self._calculate_with_tools("rule_of_72", rate_percent=rate_percent)
                return f"With a {rate_percent:.1f}% return, your investment will double in approximately {result:.1f} years."
            
            elif "monthly" in message_lower and "save" in message_lower:
                years_to_retirement = self.profile.retirement_age - self.profile.age
                target_amount = self.profile.retirement_goal / 0.04
                result = self._calculate_with_tools("monthly_savings_needed",
                    target_amount=target_amount,
                    years=years_to_retirement,
                    annual_return=self.profile.expected_return
                )
                return f"To reach your retirement goal, you should save approximately ${result:,.2f} per month."
            
            else:
                # For other questions, provide general advice
                prompt = ChatPromptTemplate.from_messages([
                    ("system", f"""You are a financial advisor. The user has provided this profile:
                    Age: {self.profile.age}
                    Income: ${self.profile.income:,.2f}
                    Current Savings: ${self.profile.current_savings:,.2f}
                    Monthly Savings: ${self.profile.monthly_savings:,.2f}
                    Retirement Age Goal: {self.profile.retirement_age}
                    Expected Return: {self.profile.expected_return*100:.1f}%
                    Risk Tolerance: {self.profile.risk_tolerance}
                    Retirement Income Goal: ${self.profile.retirement_goal:,.2f}/year
                    
                    Provide helpful, personalized financial advice based on this information."""),
                    ("user", "{message}")
                ])
                
                chain = prompt | self.llm
                response = chain.invoke({"message": message})
                return response.content

        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}. Please try rephrasing your question."