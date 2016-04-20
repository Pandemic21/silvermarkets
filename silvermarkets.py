import praw
import sqlite3
import time

#perform_action(message)
#give_starting_loan(message)
#check_balance(user)
#get_row_exists(table, column, value)
#gen_log(data)
#initialization()

def perform_action(message):
	#starting loan
	if message.body == "starting loan":
		gen_log(str(message.author) + " requested a starting loan")
		give_starting_loan(message)
	#check balance
	if message.body == "check balance": 
		gen_log(str(message.author) + " requested to check their balance")
		balance = check_balance(message.author)
		#if they have no balance
		if not balance:
			gen_log(str(message.author) + " tried to check their balance but they have no balance, message ID " + message.id)
			message.reply(text_check_balance_failed)
		else:
			gen_log(str(message.author) + " successfully checked their balance (" + str(balance) + " silver)")
			message.reply(text_check_balance_successful + str(balance))
			

	#else, they sent gibberish
	else:
		gen_log(str(message.author) + ' sent gibberish. Body = "' + message.body + '", ID = "' + message.id + '"')
		message.reply(text_gibberish)


def give_starting_loan(message):
	#if they already have a loan, they don't get another
	if get_row_exists("balances", "user", str(message.author)):
		gen_log(str(message.author) + " requested a starting loan but already has silver, message ID " + message.id)
		message.reply(text_denied_loan)
		return
	#if they don't have a loan, give them one
	gen_log(str(message.author) + ' received a starting loan')
	c.execute("INSERT INTO balances VALUES (?,?)", (str(message.author), STARTING_LOAN,))
	conn.commit()
	message.reply(text_accepted_loan)


def check_balance(user):
	#if they have no balance, tell them they have not requested a starting loan
	if not get_row_exists("balances", "user", str(user)):
		return False
	#if they do have a balance
	c.execute("SELECT silver FROM balances WHERE user=?", (str(user),))
	return c.fetchone()[0]


def get_row_exists(table, column, value):
	c.execute("SELECT count(*) FROM "+table+" WHERE "+column+"=?", (value,))
	data = c.fetchone()[0]
	if data==0:
		return False
	else:
		return True


def gen_log(data):
	f = open(LOGFILE, 'a')
	datetime =  str(time.strftime("%Y/%m/%d")) + " " + str(time.strftime("%H:%M:%S"))
	f.write(datetime + ": " + data + "\n")
	f.close()
	print datetime + ": " + data


def initialization():
	#create tables if they don't exist
	c.execute("CREATE TABLE IF NOT EXISTS balances (user text, silver text)")
	conn.commit()
	gen_log("Starting ......................")
	r = praw.Reddit("test by /u/pandemic21")
	r.login(USERNAME,PASSWORD,disable_warning="True")
	return r


# MAIN ###########################################################################

# Constants
USERNAME=""
PASSWORD=""
STARTING_LOAN="500"
LOGFILE='/home/pandemic/Documents/scripts/silvermarket/silvermarket.log'
conn = sqlite3.connect('/home/pandemic/Documents/scripts/silvermarket/silvermarket.db')
c = conn.cursor()
r = initialization()

# Message strings
text_denied_loan = "Your request for a starting loan has been denied on the grounds that you've already received a starting loan." 
text_accepted_loan = "Your request for a staritng loan has been approved! You have " + STARTING_LOAN + " silver."
text_gibberish = "Please send a valid command. Valid commands are: \n\n* starting loan\n* check balance\n\nPlease send one of those exact commands to me."
text_check_balance_failed = 'You have no balance. Try requested a starting loan by sending the command "starting loan" to me.'
text_check_balance_successful = 'Your balance is '

messages = r.get_unread()

for message in messages:
	print message.body
	perform_action(message)	
	message.mark_as_read()
	#print message.author
	#print

