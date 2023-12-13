import psycopg2
import logging
import DockerSecrets

logger = logging.getLogger('CC')

class Database:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self,dbName="postgres",user="postgres",host="postgres",pw=DockerSecrets.getDatabasePW(),mock=False):
        if (mock):
            return
        self.con = psycopg2.connect(f"dbname='{dbName}' user='{user}' host='{host}' password='{pw}'")
        self.cur = self.con.cursor()
        try:
            logger.info(self.con)
            logger.info(self.con.closed)
        except:
            logger.info("error")

    def DeInit(self):
        self.con.close()
    
    def UserExists(self,sub : str) -> bool:
        self.cur.execute(f"select 1 from Users where Users.sub = '{sub}'")
        return self.cur.fetchone() is not None

    # Get the User ID for a given sub String
    # If the User is new create that User
    def getUserIDbySUB(self, sub : str):
        if (self.UserExists(sub)):
            #Get User ID
            self.cur.execute(f"select id from Users where Users.sub = '{sub}'")
            return self.cur.fetchone()[0]
        else:
            #New User
            self.cur.execute(f"insert into Users(sub) VALUES ('{sub}') returning id;")
            id = self.cur.fetchone()[0]
            self.con.commit()
            return id