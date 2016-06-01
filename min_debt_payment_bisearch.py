#params
balance = 320000
annualInterestRate = 0.2
lower = balance / 12.0
upper = (balance * (1  + annualInterestRate / 12) ** 12) / 12.0
eps = 0.01

def get_final_balance(min_pay, balance):
	"""
	Calculates debt balance after a year 
	
	Args:
		min_pay: float - Monthly payment
		balance: int - Initial balance
	Return:
		float - end balance
	"""
    balance1 = balance
    for i in range(12):
        #print "Month: %d" %(i+1)
        #print "Minimum monthly payment: %s" %round(min_pay,2)
        balance1 = balance1 - min_pay
        balance1 = (1 + mi) * balance1
    return balance1

mi = annualInterestRate / 12.0
min_pay = (lower + upper) / 2.0
while True:
    #print min_pay
    final_balance = get_final_balance(min_pay, balance)
    #print final_balance
    if final_balance < 0:
        upper = min_pay
    else:
        lower = min_pay
    min_pay_new = (lower + upper) / 2.0
    if abs(min_pay - min_pay_new) < 0.01:
        print "Lowest Payment: %s" %round(min_pay_new, 2)
        break
    else:
        min_pay = min_pay_new