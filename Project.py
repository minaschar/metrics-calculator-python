


class Project:

   path = ''
   name = ''
   
    
   def __init__(self,p,n):
     self.path = p
     self.name = n

   @staticmethod
   def  createProject(p,n):
           return Project(p,n)
     

   def getPath(self):
        return self.path


   def getName(self):
        return self.name


   







