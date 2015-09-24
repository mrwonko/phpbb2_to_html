from phpbb2_to_html import convert

pw = raw_input( "password: " )
convert(
    host="127.0.0.1",
    port=3306,
    db="darth-arth",
    user="root",
    passwd=pw
    )
