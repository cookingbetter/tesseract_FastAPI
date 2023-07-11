amount = '1 910,00 Р'

amount = amount[:-1].split(',')

if len(amount[0]) > 3:
    amount_many = amount[0].split()
    amount[0] = amount_many[0] + amount_many[1]

amount = amount[0] + '.' + amount[1]

if amount[-1] == ' ':
    amount = amount[:-1]

result = float(amount)


print(result)