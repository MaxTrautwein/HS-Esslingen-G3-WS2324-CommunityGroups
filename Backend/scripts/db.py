import psycopg2
import logging
import DockerSecrets
import json
from typing import Optional

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

    # Create a New User by Providing the KeyCloak User Info
    def CreateUser(self,userinfo : json) -> int:
        self.cur.execute(f"insert into Users(sub, username) VALUES ('{userinfo['sub']}','{userinfo['name']}') returning id;")
        id = self.cur.fetchone()[0]
        self.con.commit()
        return id


    # Get the User ID for a given sub String
    # If the User is new create that User
    def getUserIDbySUB(self, sub : str) -> Optional[int]:
        if (self.UserExists(sub)):
            #Get User ID
            self.cur.execute(f"select id from Users where Users.sub = '{sub}'")
            return self.cur.fetchone()[0]
        return None  
    
    def getUserNameByID(self,userID : int) -> str:
        self.cur.execute(f"select username from Users where Users.sub = '{userID}'")
        return self.cur.fetchone()[0]

    # Privae Messages Chat "Room"'s
    def getDirectMessageChatRooms(self,userID : int):
        self.cur.execute(f"select DISTINCT sender,target from DirectMessages where DirectMessages.sender = '{userID}' or DirectMessages.target = '{userID}'")
        Rooms = self.cur.fetchall()
        result = []
        for room in Rooms:
            # Get the Other User ID
            otherUser = room[0]
            if userID == room[0]:
                otherUser = room[1]
            result.append({"user_id":otherUser,"username":self.getUserNameByID(otherUser)})
        return result
