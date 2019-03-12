import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv") as csvfile:
        csvf=csv.reader(csvfile)
        for isbn,title,author,year in csvf:
            db.execute("INSERT INTO books(isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
            print(f"{isbn},{title},{author},{year} is added")
        db.commit()


if __name__=='__main__':
    main() 