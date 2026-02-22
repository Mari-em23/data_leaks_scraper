
import sqlite3
from pathlib import Path
my_connection = sqlite3.connect('leaks.db') # .connect(':memory:') # this allows my database to be stored in RAM so that every time this file is executed it will recreate the table
my_cursor = my_connection.cursor() 

# ___________________________________________________________________________________________________________________________________________#
                                                           
                                                            ### For Telegram data ###
# ___________________________________________________________________________________________________________________________________________#


def create_domains_table():

    my_cursor.execute("""CREATE TABLE IF NOT EXISTS domains (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain_name TEXT UNIQUE
                      );
                    """)
    my_connection.commit()
    
def create_telegram_leaks_table():
  
  my_cursor.execute("""CREATE TABLE IF NOT EXISTS telegram_leaks (
                      id TEXT PRIMARY KEY,
                      channel_url TEXT NOT NULL,
                      message_id INTEGER NOT NULL,
                      leak_name TEXT,
                      leak_description TEXT,
                      raw_text TEXT,
                      leak_date DATETIME,
                      leak_link TEXT,
                      leak_image BLOB
                    );
                  """)
  my_connection.commit()

def create_telegram_leak_domains_table():

    my_cursor.execute("""CREATE TABLE IF NOT EXISTS telegram_leak_domains (
                      leak_id TEXT NOT NULL,
                      domain_id INTEGER NOT NULL,
                      PRIMARY KEY (leak_id, domain_id),
                      FOREIGN KEY(leak_id) REFERENCES telegram_leaks(id) ON DELETE CASCADE,
                      FOREIGN KEY(domain_id) REFERENCES domains(id) ON DELETE CASCADE
                    );
                  """)
    my_connection.commit()

def create_last_seen_messages_table():

    my_cursor.execute("""CREATE TABLE IF NOT EXISTS last_seen_messages (
                        channel_url TEXT PRIMARY KEY, 
                        last_seen_id INTEGER
                    );
                  """)
    my_connection.commit()


# Adding "OR IGNORE" keyword prevents duplicate posts to be inserted
def add_telegram_leak(info):

    my_cursor.execute("""INSERT OR IGNORE INTO telegram_leaks VALUES(
                        :leak_id,
                        :channel_url,
                        :message_id,
                        :leak_name,
                        :leak_description,
                        :raw_text,
                        :leak_date,
                        :leak_link,
                        :leak_image_bytes
                      );
                    """, {'leak_id': info['id'], 'channel_url': info['channel_url'], 'message_id': info['message_id'], 'leak_name': info['leak_name'], 'leak_description': info['description'],'raw_text':info['raw_text'], 'leak_date': info['date'], 'leak_link': info['link'], 'leak_image_bytes': info['image_bytes']})
    my_connection.commit()

def add_domain(domain_name, leak_id):

    my_cursor.execute(
        "INSERT OR IGNORE INTO domains (domain_name) VALUES (:domain_name)",
        {'domain_name': domain_name}
    )

    my_cursor.execute(
        "SELECT id FROM domains WHERE domain_name = :domain_name",
        {'domain_name': domain_name}

    )
    domain_id = my_cursor.fetchone()[0]

    my_cursor.execute(
        "INSERT OR IGNORE INTO telegram_leak_domains (leak_id, domain_id) VALUES (:leak_id, :domain_id)",
        {'leak_id': leak_id, 'domain_id': domain_id}
    )

    my_connection.commit()



def update_last_seen(channel_url, message_id):

    my_cursor.execute("SELECT last_seen_id FROM last_seen_messages WHERE channel_url = :channel_url", {'channel_url': channel_url})
    row = my_cursor.fetchone()
    
    if row is None:
        # first time processing this channel
        my_cursor.execute(
            "INSERT INTO last_seen_messages (channel_url, last_seen_id) VALUES (:channel_url, :last_seen_id)",
            {'channel_url': channel_url, 'last_seen_id': message_id})
    else:
        # only update if new message is newer
        my_cursor.execute(
            "UPDATE last_seen_messages SET last_seen_id = :message_id WHERE channel_url = :channel_url",
            {'channel_url': channel_url, 'message_id': message_id}
        )
    my_connection.commit()

def to_be_updated(channel_url, message_id):

    my_cursor.execute("SELECT last_seen_id FROM last_seen_messages WHERE channel_url = :channel_url", {'channel_url': channel_url})
    row = my_cursor.fetchone()
    return row is None or int(row[0]) < message_id

# ___________________________________________________________________________________________________________________________________________#
                                                           
                                                            ### For Forums data ###
# ___________________________________________________________________________________________________________________________________________#

def create_forums_leaks_table():

    my_cursor.execute("""CREATE TABLE IF NOT EXISTS forums_leaks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        forums_website TEXT,
                        author TEXT,
                        forum TEXT,
                        link TEXT UNIQUE,
                        post_date TEXT,
                        screenshot_path TEXT
                      )
                  """)
    my_connection.commit()

def add_forums_leaks(posts): 
    for post_info in posts:

        my_cursor.execute ("""
            INSERT OR IGNORE INTO forums_leaks
            (name, forums_website, author, forum, link, post_date, screenshot_path)
            VALUES (:title, :forums_website, :author, :forum, :link, :post_date, :screenshot)
        """, {'title':post_info['title'],'forums_website':post_info['forums_website'],'author':post_info['author'],'forum':post_info['forum'],'link':post_info['link'],'post_date':post_info['post_date'],'screenshot':post_info['screenshot']})
           
    
    my_connection.commit()
   

def main():

    create_telegram_leaks_table()
    create_domains_table()
    create_telegram_leak_domains_table()
    create_last_seen_messages_table()
    create_forums_leaks_table()

main()