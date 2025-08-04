# formulas.py
import math

def future_value(pv, rate, n):
    """Calculate future value: FV = PV × (1 + r)^n"""
    return pv * (1 + rate) ** n

def present_value(fv, rate, n):
    """Calculate present value: PV = FV / (1 + r)^n"""
    return fv / (1 + rate) ** n

def fv_annuity(pmt, rate, n):
    """Calculate future value of annuity: FV = PMT × [(1 + r)^n – 1] / r"""
    if rate == 0:
        return pmt * n
    return pmt * ((1 + rate) ** n - 1) / rate

def pv_annuity(pmt, rate, n):
    """Calculate present value of annuity: PV = PMT × [1 – (1 + r)^(–n)] / r"""
    if rate == 0:
        return pmt * n
    return pmt * (1 - (1 + rate) ** -n) / rate

def nper(rate, pmt, pv, fv=0):
    """Calculate number of periods (Excel-style NPER function)"""
    if rate == 0:
        return -(fv + pv) / pmt
    
    # NPER = ln((pmt - fv*rate) / (pmt + pv*rate)) / ln(1 + rate)
    numerator = (pmt - fv * rate) / (pmt + pv * rate)
    if numerator <= 0:
        return float('inf')  # No solution
    
    return math.log(numerator) / math.log(1 + rate)

def rule_of_72(rate_percent):
    """Estimate years to double investment: Years ≈ 72 / rate%"""
    return 72 / rate_percent

def calculate_retirement_age(current_age, current_savings, monthly_savings, target_amount, annual_return):
    """Calculate when someone can retire based on their savings plan"""
    monthly_rate = annual_return / 12
    monthly_target = target_amount
    
    # Use NPER to find months needed
    months_needed = nper(monthly_rate, -monthly_savings, -current_savings, monthly_target)
    
    if months_needed == float('inf') or months_needed < 0:
        return None
    
    return current_age + (months_needed / 12)

def calculate_savings_longevity(initial_amount, monthly_withdrawal, annual_return):
    """Calculate how long savings will last with regular withdrawals"""
    monthly_rate = annual_return / 12
    
    # Use NPER: how long until balance reaches 0
    months = nper(monthly_rate, monthly_withdrawal, -initial_amount, 0)
    
    if months == float('inf') or months < 0:
        return float('inf')  # Money lasts forever or grows
    
    return months / 12  # Convert to years

def monthly_savings_needed(target_amount, years, annual_return):
    """Calculate monthly savings needed to reach a target"""
    monthly_rate = annual_return / 12
    months = years * 12
    
    if monthly_rate == 0:
        return target_amount / months
    
    # PMT = FV * r / [(1 + r)^n - 1]
    return target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)