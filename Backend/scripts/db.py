import psycopg2
import logging
import DockerSecrets
import json
from datetime import datetime
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
        self.cur.execute("""
        insert into Users(sub, username) VALUES (%s,%s) returning id;
        """,
        (userinfo['sub'],userinfo['preferred_username']))
        
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
        self.cur.execute(f"select username from Users where Users.id = '{userID}'")
        return self.cur.fetchone()[0]

    def getUserIDbyName(self,username : str) -> Optional[int]:
        #It Needs to be a Tulpe.... That us such an Frustrating Error to debug :( 
        self.cur.execute("select id from Users where username = %s",(username,))
        res = self.cur.fetchone()
        if (res is not None):
            return res[0]
        return None 

    # Privae Messages Chat "Room"'s
    def getDirectMessageChatRooms(self,userID : int):
        self.cur.execute(f"select DISTINCT sender,receiver from DirectMessages where DirectMessages.sender = '{userID}' or DirectMessages.receiver = '{userID}'")
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
    
    def MessagesToJsonArray(self,messages):
        result = []
        for msg in messages:
            recTime = msg[5]
            if (recTime is None):
                recTime = ""
            else:
                recTime = msg[5].strftime("%d.%m.%Y %H:%M")
            readTime = msg[6]
            if (readTime is None):
                readTime = ""
            else:
                readTime = msg[6].strftime("%d.%m.%Y %H:%M")
            result.append({"id":msg[0], 
                           "sender":self.getUserNameByID(msg[1]),
                           "receiver":self.getUserNameByID(msg[2]), 
                           "msg":msg[3],
                           "sendTime":msg[4].strftime("%d.%m.%Y %H:%M"),
                           "recTime":recTime,
                           "readTime":readTime
                           })
        return result

    # Proably rather ineffeciant Use "GetChatMsgs" For a more Optimzed Implementation
    def GetAllChatMsg(self,sender : int ,receiver : int ):
        self.cur.execute("""
        select * from DirectMessages where
        DirectMessages.sender = %s or DirectMessages.receiver = %s or
        DirectMessages.receiver = %s or DirectMessages.sender = %s               
        ORDER BY DirectMessages.id
        """,
        (sender,receiver,sender,receiver))
        messages = self.cur.fetchall()
        return self.MessagesToJsonArray(messages)
    
    # If cnt is negative get before that point
    # If it is positive after
    def GetChatMsgs(self,sender : int ,receiver : int ,baseline : int, cnt : int):
        limit = abs(cnt)
        if (cnt > 0):
            self.cur.execute("""
            select * from DirectMessages where
            (DirectMessages.sender = %s or DirectMessages.receiver = %s or
            DirectMessages.receiver = %s or DirectMessages.sender = %s) and
            DirectMessages.id > %s             
            ORDER BY DirectMessages.id
            LIMIT %s
            """,
            (sender,receiver,sender,receiver,baseline,limit))
        else:
            self.cur.execute("""
            select * from DirectMessages where
            (DirectMessages.sender = %s or DirectMessages.receiver = %s or
            DirectMessages.receiver = %s or DirectMessages.sender = %s) and
            DirectMessages.id < %s             
            ORDER BY DirectMessages.id
            LIMIT %s
            """,
            (sender,receiver,sender,receiver,baseline,limit))
        messages = self.cur.fetchall()
        return self.MessagesToJsonArray(messages)