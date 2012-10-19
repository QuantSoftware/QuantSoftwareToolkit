import csv
# import dateutil.parser as dp
import string


def csv_converter(inputfile, outputfile):
    actualheader = ['Symbol', 'Name', 'Type', 'Date', 'Shares', 'Price', 'Cash value', 'Commission', 'Notes']

    reader = csv.reader(open(inputfile, 'r'), delimiter=',')
    header = reader.next()
    print "Header : ", header
    input_str = []
    for row in reader:
        input_str.append(row)
    input_str = input_str[::-1]

    writer = csv.writer(open(outputfile, 'wb'), delimiter=',')
    writer.writerow(actualheader)

    for row in input_str[:]:
        # print row
        if row[0] != '--':
            date = row[0]
        else:
            date = row[1]

        Commission = '0'
        Notes = ''
        cashvalue = row[12]

        if row[9] == 'BRKB':
            row[9] = 'BRK.B'

        if row[7] == 'Close Short':
            continue

        if row[7] == 'Sale ':
            ordertype = 'Sell'
            symbol = row[9]
            name = row[8]
            shares = str(int(row[10]) * (-1))
            price = row[11]
        elif row[7] == 'Purchase ':
            ordertype = 'Buy'
            symbol = row[9]
            name = row[8]
            shares = row[10]
            price = row[11]
        elif row[7] == 'Dividend' or row[7] == 'Bank Interest' \
                 or row[7] == 'Interest Charge' or row[7] == 'Paymnt In Lieu' \
                 or row[7] == 'Annual Charge' or row[7] == 'Funds Transfer':
            ordertype = 'Deposit Cash'
            symbol = ''
            name = row[7]
            shares = ''
            price = ''
        elif row[7] == 'Stock Dividend' or row[7] == 'DUDB':
            ordertype = 'Buy'
            symbol = row[9]
            name = 'Dividend'
            shares = row[10]
            price = '0'
        elif row[7] == 'Journal Entry':
            if row[10] != '--':
                ordertype = 'Buy'
                symbol = row[9]
                name = row[7] + row[8]
                shares = row[10]
                price = '0'
            else:
                ordertype = 'Deposit Cash'
                symbol = ''
                name = 'Deposit Cash'
                shares = ''
                price = ''
        else:
            name = row[7] + row[8]
            if row[10] == '--':
                shares = ''
                ordertype = 'Deposit Cash'
                price = ''
                symbol = ''
            else:
                shares = row[10]
                ordertype = 'Buy'
                if row[11] == '--':
                    price = '0'
                else:
                    price = row[11]
                symbol = row[9]

        shares = string.replace(shares, ',', '')
        price = string.replace(price, ',', '')
        cashvalue = string.replace(cashvalue, ',', '')

        row_to_enter = [symbol, name, ordertype, date, shares, price, cashvalue, Commission, Notes]
        # print row_to_enter
        writer.writerow(row_to_enter)

if __name__ == "__main__":
    inputfile = "./Settled.csv"
    outputfile = 'trans.csv'
    csv_converter(inputfile, outputfile)
    print "Done"
