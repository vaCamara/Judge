from tkinter import *
from tkinter import filedialog
from PIL import ImageTk
from PIL import Image
import os
import sqlite3
import matplotlib.pyplot as plt
import subprocess

width = 750
height = 750
path_directory = os.getcwd()


class ImagePrinter:
    def __init__(self, name_image, number_insects):
        self.root = Toplevel()
        self.root.title(name_image)
        self.canvas = Canvas(self.root, width=width, height=height)
        self.canvas.pack()
        img = Image.open(name_image)
        img = img.resize((width, height), Image.ANTIALIAS)
        self.canvas.imageObject = ImageTk.PhotoImage(img)
        self.canvas.create_image(width/2, height/2, image=self.canvas.imageObject)
        Label(self.root, text="Number of insects found: "+str(number_insects)).pack()


class Decider:
    def __init__(self):
        self.over = False
        # creation of the database
        self.nom_bdd = "donnees_images.sq3"
        self.connector = sqlite3.connect(self.nom_bdd)
        self.cursor = self.connector.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS donnees_insectes ( numero INTEGER, nom TEXT, "
                            "ok BOOLEAN, nb_insectes INTEGER)")

        # delete the old occurrences (should I ?)
        self.cursor.execute("DELETE FROM donnees_insectes")
        self.connector.commit()

        # creation of the new window
        self.root = Toplevel()
        self.root.title("Judging...")
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        # canvas for the images
        self.canvas = Canvas(self.root, width=width, height=height)
        self.canvas.pack()

        # entrée nombre insectes
        self.entree_insectes = Entry(self.root)
        self.entree_insectes.bind("<Return>", self.evaluate_nb_insects)
        self.entree_insectes.pack()
        self.nb_insectes = 0

        # creation of the lists of images (necessary for Python which needs a reference when using itemconfigure,
        # cf update_image)
        self.image_names = get_all_images()
        self.images = []
        for name in self.image_names:
            img = Image.open(name)
            img = img.resize((width, height), Image.ANTIALIAS)
            self.images.append(ImageTk.PhotoImage(img))
        self.id_image = 0

        # if we have at least one image, we fill the canvas with the first one
        if len(self.images) > 0:
            self.item = self.canvas.create_image(width/2, height/2, image=self.images[0])
        else:
            self.item = None

        # creating the buttons OK/NOK
        Button(self.root, text="Ok", command=lambda: self.update_image(True)).pack()
        Button(self.root, text="Not Ok", command=lambda: self.update_image(False)).pack()

    def update_image(self, value):
        # registering the data
        if not self.over:
            self.cursor.execute("INSERT INTO donnees_insectes(numero, nom, ok, nb_insectes) VALUES(?,?,?, ?)",
                                (self.id_image, self.image_names[self.id_image], value, self.nb_insectes))
            self.connector.commit()
            self.nb_insectes = 0

        # printing the new image
        if len(self.image_names) > self.id_image+1:
            self.id_image += 1
            self.canvas.itemconfig(self.item, image=self.images[self.id_image])
        else:
            self.over = True
            self.cursor.execute("SELECT * FROM donnees_insectes WHERE ok")
            # printing the result
            root_results = Toplevel()
            root_results.title("Results")
            number_ok = len(self.cursor.fetchall())
            Label(root_results, text="Number of good images:" + str(number_ok)).pack()
            Label(root_results, text="Number of wrong images:" + str(len(self.images) - number_ok)).pack()

            self.cursor.execute("SELECT nom, nb_insectes FROM donnees_insectes WHERE NOT ok")
            result = self.cursor.fetchall()
            Button(root_results, text="Distribution of wrong images", command=lambda: show_plot(result)).pack()

            self.cursor.execute("SELECT nom, nb_insectes FROM donnees_insectes WHERE NOT ok")
            wrong_images = self.cursor.fetchall()
            Button(root_results, text="Shows the wrong images", command=lambda: show_wrong_images(wrong_images)).pack()

            self.close_window()

            def show_plot(result_found):
                nom, nb_insectes = [], []
                for k in result_found:
                    nom.append(k[0])
                    nb_insectes.append(k[1])
                plt.scatter(nom, nb_insectes, color='darkred', marker='x')
                plt.title("Number of insects for each wrong image")
                plt.show()

            # not working images
            def show_wrong_images(wrong_images_found):
                for wrong_image in wrong_images_found:
                    ImagePrinter(wrong_image[0], wrong_image[1])

    def close_window(self):
        self.cursor.close()
        self.connector.close()
        self.root.destroy()

    def evaluate_nb_insects(self, event):
        self.nb_insectes = eval(self.entree_insectes.get())


def choose_directory():
    global path_directory
    path_directory = filedialog.askdirectory()
    nameDirectory.configure(text="Chosen directory: " + path_directory)


def get_all_images():
    list_images = os.listdir(path_directory)
    result = []
    for file in list_images:
        if "jpg" in file or "png" in file or "webp" in file or "jpeg" in file:
            result.append(file)
    return result


def decider():
    Decider()


def docker():
    subprocess.call(["sh", "docker.sh"])


def change_size_menu():
    root_menu = Toplevel()
    Label(root_menu, text="Change size of height/width").pack()
    w = Spinbox(root_menu, from_=100, to=1000)
    w.pack()
    Button(root_menu, text="OK", command=lambda: change_size(int(w.get()), root_menu)).pack()


def change_size(size, root_a):
    global width, height
    width = size
    height = size
    root_a.destroy()


if __name__ == "__main__":
    root = Tk()
    root.title("Judge")
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Change image size", command=change_size_menu)
    menubar.add_cascade(label="Images", menu=filemenu)
    Label(root, text="JUDGE is the Ultimate Decider for Graphical Elements").pack()
    Button(root, text="Launch study", command=decider).pack()
    Button(root, text='Choose directory', command=choose_directory).pack()
    Button(root, text='Launch docker script', command=docker).pack()
    nameDirectory = Label(root).pack()
    root.config(menu=menubar)
    root.mainloop()
