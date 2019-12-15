import decimal as dec

def decimalAverage(num1, num2):
    n1 = dec.Decimal(str(num1))
    n2 = dec.Decimal(str(num2))
    average = (n1 + n2) / dec.Decimal('2.0')
    return average.quantize(dec.Decimal('.1'), rounding=dec.ROUND_UP)
