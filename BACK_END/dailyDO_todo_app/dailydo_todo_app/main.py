from  fastapi import FastAPI
from sqlmodel import Field, SQLModel, Session,create_engine
from dailydo_todo_app import setting

#Database creation

#Create Model (models(DATA MODEL) (TABLE MODEL))
class Todo (SQLModel,table=True): # Table Model
    #Data model
    id: int | None = Field( default=None,primary_key=True)    #ID is a promary key and PK MUST BE UNIQUE
    content: str = Field(index=True ,min_length=3,max_length=54)
    is_completed: bool = Field()

#Craete Engin (Database connection)
connection_string : str =  str (setting.DATABASE_URL).replace("postgresql" , "postgresql + psycopg")

#enginne  only one for whole application
engine = create_engine(connection_string ,connect_args={"sslmode": "require"},pool_recycle=300
,pool_size=10 ,echo = True)  #(like trranslater) connection string convert ORM comands in SQLand then given to db



SQLModel.metadata.create_all(engine)

todo1 : Todo = Todo(content='first task')
todo2 : Todo = Todo(content='second task')

session = Session(engine)

session.add(todo1)
session.add(todo2)
print("f' Before commit {todo1}")
session.commit()  
print("f' After commit {todo1}")
session.close()


app = FastAPI() #create instance(class)


#roots

@app.get('/')
async def root():
    return {"message" : "Welcome yo dailyDo_todo_app"}

@app.get('/todos/')
async def read_todo():
    return {"content": "dummy todo"}
