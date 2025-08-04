# Financial Planning Agent

This is a **AI-powered retirement planning advisor**. Built using LangChain, Streamlit, and Ollama (Mistral), this assistant helps users calculate retirement savings, estimate future value, and make informed financial decisions using well-established financial formulas.

---

## 📦 Features

- 🔍 **Personalized Retirement Planning**  
  Answer a few questions and receive a customized retirement summary with surplus/deficit insights.

- 📊 **Smart Financial Calculators**  
  Tools include:
  - Future Value Calculator
  - Present Value Calculator
  - Rule of 72 Estimator
  - Retirement Age Estimator
  - Savings Longevity Estimator
  - Monthly Savings Requirement

- 🧠 **Conversational Agent**  
  Uses LangChain and Ollama's `mistral` model to respond naturally to user queries.

---

## 🧰 Tech Stack

- 🧱 [LangChain](https://www.langchain.com/)
- 🤖 [Ollama](https://ollama.com/) (with `mistral` model)
- 🎨 [Streamlit](https://streamlit.io/)
- 🧮 Python financial functions in `formulas.py`

---

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/financial-planning-agent.git
cd financial-planning-agent
```
### 2. Set Up Python Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Run Ollama with Mistral
```bash
ollama run mistral
```
### Launch the StreamLit App
```bash
streamlit run finance_assistant/app.py
```
### To run tests
```bash
pytest tests/test_formulas.py
```
Folder Structure
├── advisor_agent.py          # LangChain-based financial advisor logic
├── app.py                    # Streamlit app launcher
├── formulas.py               # Financial formulas used by the advisor
├── ui_streamlit.py           # Streamlit UI components and layout
├── test_formulas.py          # Unit tests for financial formulas (pytest-compatible)
├── requirements.txt          # Project dependencies
└── README.md                 # Documentation and usage instructions
