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
        # Use psycopg2 Parameter to ensure that the name is sanitized 
        self.cur.execute(f"insert into Users(sub, username) VALUES ('{userinfo['sub']}',%s) returning id;",(userinfo['preferred_username']))
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
    
    def getUserIDbyName(self,username : str) -> Optional[int]:
        self.cur.execute(f"select id from Users where Users.username = %s",username)
        res = self.cur.fetchone()
        if (res is not None):
            return res[0]
        return None 

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
    
    def SendDirectMessageTo(self,sender : int ,receiver : int, msg : str):
        # Use psycopg2 Parameter to ensure that the msg is sanitized 
        self.cur.execute("""
        INSERT INTO DirectMessages (sender, receiver, msg, sendTime)
        VALUES (%s, %s, %s,now());
        """,
        (sender,receiver,msg))
        self.con.commit()
    
    def UpdateReciveTime(self, msgId: int, userID : int):
        self.cur.execute(f"update directmessages set recTime = now() where id = {msgId} and receiver = {userID}")
        self.con.commit()

    def UpdateReadTime(self, msgId: int, userID : int):
        self.cur.execute(f"update directmessages set readTime = now() where id = {msgId} and receiver = {userID}")
        self.con.commit()
    
    # Proably rather ineffeciant but its a first step
    # TODO Save the Messages on the device and request new ones
    def GetAllChatMsg(self,sender : int ,receiver : int ):
        self.cur.execute("""
        select * from DirectMessages where
        DirectMessages.sender = %s or DirectMessages.target = %s or
        DirectMessages.target = %s or DirectMessages.sender = %s or                
        order by DirectMessages.id
        """,
        (sender,receiver,sender,receiver))
        messages = self.cur.fetchall()
        result = []
        for msg in messages:
            result.append({"id":msg[0], 
                           "sender":self.getUserNameByID(msg[1]),
                           "receiver":self.getUserNameByID(msg[2]), 
                           "msg":msg[3],
                           "sendTime":msg[4],
                           "recTime":msg[5],
                           "readTime":msg[6]
                           })
        return result