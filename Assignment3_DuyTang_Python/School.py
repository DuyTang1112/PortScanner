import sqlite3 as db
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk

'''
DAL Area
'''
class SchoolDbAccessLayer:
    def __init__(self):
        self.is_conn_open = False
        self.__connect__()
    def __connect__(self):
        if not self.is_conn_open:
            self.conn = db.connect('school.db')
            self.conn.row_factory = db.Row
            self.cur = self.conn.cursor()
            self.is_conn_open = True
    def __clost_connection_(self):
        if self.is_conn_open:
            self.conn.commit()
            self.conn.close()
            self.is_conn_open = False
    def __del__(self):
        self.__clost_connection_() 

class StudentDAL(SchoolDbAccessLayer):
    def create(self, id, name):
        self.cur.execute('INSERT INTO student VALUES(?, ?)', (id, name))
        self.conn.commit()
    def read(self, id = None, name = None):
        if id == None:
            if name == None:
                self.cur.execute('SELECT * FROM student')
            else:
                self.cur.execute("SELECT * FROM student WHERE Name=?", (name,))
        elif name != None:
            self.cur.execute("SELECT * FROM student WHERE Id=? AND Name=?", (id, name))
        else:
            self.cur.execute("SELECT * FROM student WHERE Id=?", (id,))
        return self.cur.fetchall()
    def update(self, id, name):
        self.cur.execute('UPDATE student SET Name=? WHERE Id=?', (name, id))
        self.conn.commit()
    def delete(self, id):
        self.cur.execute('DELETE FROM student WHERE id=?', (id,))
        self.conn.commit()

class TeacherDAL(SchoolDbAccessLayer):
    def create(self, id, name):
        self.cur.execute('INSERT INTO teacher VALUES(?, ?)', (id, name))
        self.conn.commit()
    def read(self, id = None, name = None):
        if id == None:
            if name == None:
                self.cur.execute('SELECT * FROM teacher')
            else:
                self.cur.execute("SELECT * FROM teacher WHERE Name=?", (name,))
        elif name != None:
            self.cur.execute("SELECT * FROM teacher WHERE Id=? AND Name=?", (id, name))
        else:
            self.cur.execute("SELECT * FROM teacher WHERE Id=?", (id,))
        return self.cur.fetchall()
    def update(self, id, name):
        self.cur.execute('UPDATE teacher SET Name=? WHERE Id=?', (name, id))
        self.conn.commit()
    def delete(self, id):
        self.cur.execute('DELETE FROM teacher WHERE id=?', (id,))
        self.conn.commit()

class CourseDAL(SchoolDbAccessLayer):
    def create(self, num, name, credits, teacher_id):
        self.cur.execute('INSERT INTO course VALUES(?, ?, ?, ?)', (num, name, credits, teacher_id))
        self.conn.commit()
    def read(self, number = None, teacher_id = None):
        if number == None:
            if teacher_id == None:
                self.cur.execute('SELECT * FROM course')
            else:
                self.cur.execute("SELECT * FROM course WHERE TeacherId=?", (teacher_id,))
        elif teacher_id != None:
            self.cur.execute("SELECT * FROM course WHERE Number=? AND TeacherId=?", (number, teacher_id))
        else:
            self.cur.execute("SELECT * FROM course WHERE Number=?", (number,))
        return self.cur.fetchall()
    def update(self, number, name, teacher_id):
        self.cur.execute('UPDATE course SET Name=?, TeacherId=? WHERE Number=?', (name, teacher_id, number))
        self.conn.commit()
    def delete(self, number):
        self.cur.execute('DELETE FROM course WHERE Number=?', (number,))
        self.conn.commit()

class EnrollmentDAL(SchoolDbAccessLayer):
    def create(self, student_id, course_id):
        self.cur.execute('INSERT INTO enrolled VALUES(?, ?)', (student_id, course_id))
        self.conn.commit()
    def read(self, student_id = None, course_id = None):
        if student_id == None:
            if course_id == None:
                self.cur.execute('SELECT * FROM enrolled')
            else:
                self.cur.execute("SELECT * FROM enrolled WHERE CourseNumber=?", (course_id,))
        elif course_id != None:
            self.cur.execute("SELECT * FROM enrolled WHERE CourseNumber=? AND StudentId=?", (course_id, studert_id))
        else:
            self.cur.execute("SELECT * FROM enrolled WHERE CourseNumber=?", (course_id,))
        return self.cur.fetchall()
    def query_by_teacher(self, teacher_id):
        self.cur.execute("""SELECT e.* 
        FROM enrolled e 
        JOIN course c ON e.CourseNumber = c.Number
        WHERE c.TeacherId=?""", (teacher_id,))
        return self.cur.fetchall()
    def read_all(self):
        self.cur.execute('''SELECT e.CourseNumber,
        c.Name as CourseName,
        e.StudentId,
        s.Name as StudentName,
        c.TeacherId,
        t.Name as TeacherName
        FROM enrolled e
        JOIN course c ON c.Number = e.CourseNumber
        JOIN student s ON s.Id = e.StudentId
        JOIN teacher t ON t.Id = c.TeacherId
        ''')
        return self.cur.fetchall()
    def delete(self, course_id, student_id):
        self.cur.execute("DELETE FROM enrolled WHERE CourseNumber=? AND StudentId=?", (course_id, studert_id))
        self.conn.commit()
        
"""
GUI Area
"""
class MainWindow:
    def __init__(self):
        self.sDal = StudentDAL()
        self.cDal = CourseDAL()
        self.eDal = EnrollmentDAL()
        self.__gui_init_()
    def __gui_init_(self):
        self.root = tk.Tk()
        self.root.title('Student Enrollment')
        self.om1_var = tk.StringVar()
        self.grd = tk.Frame(self.root)
        self.grd.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.treeview = ttk.Treeview(self.grd)
        self.treeview['columns'] = ('CourseNumber', 'StudentId', 'StudentName', 'TeacherId', 'TeacherName')
        self.treeview['displaycolumns'] = ('StudentName', 'TeacherName')
        self.treeview.heading('#0', text='Course Name')
        self.treeview.heading('StudentName', text='Student Name')
        self.treeview.heading('TeacherName', text='Teacher Name')
        self.treeview.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        self.treeview.bind("<Double-1>", self.tree_double_click)
        self.__update_grd_()
        self.root.mainloop()
        
    def __update_grd_(self):
        courses = self.eDal.read_all()
        print(courses)
        for row in self.treeview.get_children():
            treeview.delete(row)
        for course in courses:
            self.treeview.insert('', tk.END, text=course['CourseName'], values=(course['CourseNumber'], course['StudentId'], 
            course['StudentName'], course['TeacherId'], course['TeacherName']))
            
    def tree_double_click(self, event):
        item = self.treeview.identify('item',event.x,event.y)
        item2 = self.treeview.item(item)
        print(item2)
if __name__ == '__main__':
    wnd = MainWindow()