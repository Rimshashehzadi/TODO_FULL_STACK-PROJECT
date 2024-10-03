from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from  fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, SQLModel, Session,create_engine, select
from dailydo_todo_app import setting


#Database creation

#Create Model (models(DATA MODEL) (TABLE MODEL))
class Todo (SQLModel,table=True): # Table Model
    #Data model
    id: int | None = Field( default=None,primary_key=True)    #ID is a promary key and PK MUST BE UNIQUE
    content: str = Field(index=True ,min_length=3,max_length=54)
    is_completed: bool = Field(default=False)

#Craete Engin (Database connection)
# connection_string : str =  str (setting.DATABASE_URL).replace("postgresql" , "postgresql + psycopg")

connection_string : str = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
#enginne  only one for whole application
engine = create_engine(connection_string ,connect_args={"sslmode": "require"},pool_recycle=300
,pool_size=10 ,echo = True)  #(like trranslater) connection string convert ORM comands in SQLand then given to db

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

# SQLModel.metadata.create_all(engine)

# todo1 : Todo = Todo(content='first task')
# todo2 : Todo = Todo(content='second task')

# session = Session(engine)

# session.add(todo1)
# session.add(todo2)
# print("f' Before commit {todo1}")
# session.commit()  
# print("f' After commit {todo1}")
# session.close()
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title = "dailydo_todo_app", version = "0.1") #create instance(class)


#roots function that's call session on every API call

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

@app.get('/todos/{id}',response_model=Todo)
async def get_single_todo(id:int,session:Annotated[Session,Depends(get_session)]):
     todo = session.exec(select(Todo).where(Todo.id==id)).first()
     if todo:
          todo.id = todo.id
          todo.is_completed = todo.is_completed
          session.add(todo)
        #   session.commit()
          session.refresh(todo)
          return todo
     else:
          raise HTTPException (status_code=404,detail= "id not found")
@app.put('/todos/{id}')
async def edit_todo(todo:Todo,session:Annotated[Session , Depends(get_session)]):
     existing_todo = session.exec(select(Todo).where(Todo.id == id)).first() 
     if existing_todo:
        existing_todo.content = todo.content
        existing_todo.is_completed =  todo.is_completed
        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
     else:
          raise HTTPException(status_code=404, detail="detail not found")
     
@app.delete('/todos/{id}')
async def delete_todo(id:int,session:Annotated[Session , Depends(get_session)]):
     todo = session.exec(select(Todo).where(Todo.id == id)).first() 
     if todo:
        session.delete(todo)
        session.commit()
        session.refresh(todo)
        return {"message":"Task successfully deleted"}
     else:
          raise HTTPException(status_code=404, detail="Task not found")     
     



              
     
               
     
          
      
     
     
     
