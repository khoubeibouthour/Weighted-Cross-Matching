from os import walk, getcwd
from os.path import join
import cx_Oracle

connection = cx_Oracle.connect('python/python')
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM faces")
total = cursor.fetchone()[0]

counter = 0
for root, dirs, files in walk(join(getcwd(), "Rendered")):
    if root.split("/")[-1] == "Pics": continue
    for image in files:
        counter += 1
        print("\rUpdating " + str(counter) + " / " + str(total) + " : " + image + "          ",)
        query = "UPDATE faces SET person = '" + root.split("/")[-1] + "' WHERE filename = '" + image + "'"
        try:
            cursor.execute(query)
        except:
            print("Please check this query:\n" + query)
        # if counter > 5:
        #     cursor.close()
        #     connection.commit()
        #     connection.close()
        #     exit()
cursor.close()
connection.commit()
connection.close()
