import fitz
import os 
import zipfile

ALLOWED_IMG = set(['png', 'jpg', 'jpeg','JPG','JPEG'])

class pdftool:
    def __init__(self,dir):
        self.pdf=[]
        self.img=[]
        self.initerror=False
        try:
            files = os.listdir(dir)
            files.sort(key=lambda x:int(x.split('.')[0]))
            for file in files:
                back=os.path.splitext(file)[-1][1:]
                if back=='pdf':
                    self.pdf.append(fitz.open(os.path.join(dir,file)))
                elif back in ALLOWED_IMG:
                    self.img.append(fitz.open(os.path.join(dir,file)))
        except:
            self.initerror=True

    def zip(self,func,dir):
        zipname=os.path.join(dir,func+'.zip')
        f=zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED)
        for _, _, filenames in os.walk(dir):
            for filename in filenames:
                _,tempname=os.path.split(filename)
                if tempname.endswith("pdf") or tempname.endswith("png"):
                    f.write(os.path.join(dir,filename),tempname)
        return zipname

    def merge(self,dir):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            dir=os.path.join(dir,"merged")
            if not os.path.exists(dir):
                os.makedirs(dir)
            doc=fitz.open()
            for handle in self.pdf:
                doc.insertPDF(handle)
            output=os.path.join(dir,"merged.pdf")
            doc.save(output)
            return output
        except:
            return "error: merge fail"

    def split(self,dir,mode):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            dir=os.path.join(dir,"splitted")
            if not os.path.exists(dir):
                os.makedirs(dir)
            splitnum=1
            if mode=="pdf":
                for doc in self.pdf:
                    for page in doc:
                        newfile=fitz.open()
                        newfile.insertPDF(doc, from_page=page.number, to_page=page.number, start_at=-1)
                        newfile.save(os.path.join(dir,str(splitnum)+".pdf"))
                        splitnum+=1

            elif mode=="image":
                for doc in self.pdf:
                    for page in doc:
                        pix = page.getPixmap()
                        pix.writeImage(os.path.join(dir,str(splitnum)+".png"))
                        splitnum+=1
            
            return self.zip("splitted",dir)
        except:
            return "error: split fail"
        
    def img2pdf(self,dir,letter):
        try:
            if not self.img:
                return "error: No supported image file found"
            dir=os.path.join(dir,"img2pdf")
            if not os.path.exists(dir):
                os.makedirs(dir)
            output=os.path.join(dir,"merged"+".pdf")
            if letter:
                doc=fitz.open()
                for img in self.img:
                    pdfbytes = img.convertToPDF()
                    imgpdf = fitz.open("pdf", pdfbytes)
                    pix = imgpdf[-1].getPixmap()
                    doc.newPage()
                    doc[-1].insertImage(doc[-1].rect,pixmap=pix)

                doc.save(output)
                return output
            else:
                doc=fitz.open()
                for img in self.img:
                    pdfbytes = img.convertToPDF()
                    imgpdf = fitz.open("pdf", pdfbytes)
                    doc.insertPDF(imgpdf)
                doc.save(output)
                return output
        except:
            return "error: img2pdf fail"

    def pdf_add_img(self,dir,letter):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            if not self.img:
                return "error: No supported image file found"
            dir=os.path.join(dir,"added")
            if not os.path.exists(dir):
                os.makedirs(dir)

            doc=fitz.open()
            for handle in self.pdf:
                doc.insertPDF(handle)

            if letter:
                for img in self.img:
                    pdfbytes = img.convertToPDF()
                    imgpdf = fitz.open("pdf", pdfbytes)
                    pix = imgpdf[-1].getPixmap()
                    doc.newPage(pno=-1,width=doc[-1].rect.width,height=doc[-1].rect.height)
                    doc[-1].insertImage(doc[-1].rect,pixmap=pix)
            else:
                for img in self.img:
                    pdfbytes = img.convertToPDF()
                    imgpdf = fitz.open("pdf", pdfbytes)
                    doc.insertPDF(imgpdf)    

            output=os.path.join(dir,"added.pdf")
            doc.save(output)
            return output
        except:
            return "error: addimg fail"

    def compress(self,dir):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            dir=os.path.join(dir,"compressed")
            if not os.path.exists(dir):
                os.makedirs(dir)
            
            for doc in self.pdf:
                newfile=fitz.open()
                for page in doc:
                    pm = page.getPixmap(alpha=False)
                    pmdata=pm.getPNGdata()
                    tempimg=fitz.open("png",pmdata)
                    pdfbytes=tempimg.convertToPDF()
                    temppdf=fitz.open("pdf", pdfbytes)
                    newfile.insertPDF(temppdf)
                _,docname=os.path.split(doc.name)
                savepath=os.path.join(dir,docname)
                newfile.save(savepath)
            if len(self.pdf)>1:
                return self.zip("compressed",dir)
            else:
                return savepath
        except:
            return "error: compress fail"

    def encrypt(self,dir,ownerpass,userpass):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            dir=os.path.join(dir,"encrypted")
            if not os.path.exists(dir):
                os.makedirs(dir)

            perm = int(
                        fitz.PDF_PERM_ACCESSIBILITY # always use this
                        | fitz.PDF_PERM_PRINT # permit printing
                        | fitz.PDF_PERM_COPY  # permit copying
                        | fitz.PDF_PERM_ANNOTATE # permit annotations
                    )  
            owner_pass = ownerpass  # owner password
            user_pass = userpass  # user password
            encrypt_meth = fitz.PDF_ENCRYPT_AES_256  # strongest algorithm

            for doc in self.pdf:
                _,docname=os.path.split(doc.name)
                output=os.path.join(dir,"encrypted_"+docname)
                doc.save(
                        output,
                        encryption=encrypt_meth,  # set the encryption method
                        owner_pw=owner_pass,  # set the owner password
                        user_pw=user_pass,  # set the user password
                        permissions=perm,  # set permissions
                )

            if len(self.pdf)>1:
                return self.zip("encrypted",dir)
            else:
                return output
        except:
            return "error: encrypt fail"

    def decrypt(self,dir,password):
        try:
            if not self.pdf:
                return "error: No supported pdf file found"
            dir=os.path.join(dir,"decrypted")
            if not os.path.exists(dir):
                os.makedirs(dir)
            
            for doc in self.pdf:
                if doc.isEncrypted:
                    _,docname=os.path.split(doc.name)
                    output=os.path.join(dir,"decrypted_"+docname)
                    doc.authenticate(password)
                    doc.save(os.path.join(dir,"decrypted_"+docname))
            if len(self.pdf)>1:
                return self.zip("decrypted",dir)
            else:
                return output
        except:
            return "error: decrypt fail"

        
    def close(self):
        for file in self.pdf:
            file.close()
        for img in self.img:
            img.close()

def pdfproc(file_dir,func,**kwargs):
    tool=pdftool(file_dir)

    if tool.initerror:
        tool.close()
        return "error: unsupported file"
    if not tool.pdf and not tool.img:
        return "error: no file found"

    if func == "merge":
        r=tool.merge(file_dir)
        tool.close()
        return r
    elif func == "splitpdf":
        r=tool.split(file_dir,"pdf")
        tool.close()
        return r
    elif func == "splitimg":
        r=tool.split(file_dir,"image")
        tool.close()
        return r
    elif func == "img2pdf":
        r=tool.img2pdf(file_dir,kwargs["letter"])
        tool.close()
        return r
    elif func == "addimg":
        r=tool.pdf_add_img(file_dir,kwargs["letter"])
        tool.close()
        return r
    elif func == "compress":
        r=tool.compress(file_dir)
        tool.close()
        return r
    elif func == "encrypt":
        r=tool.encrypt(file_dir,kwargs["ownerpass"],kwargs["userpass"])
        tool.close()
        return r
    elif func == "decrypt":
        r=tool.decrypt(file_dir,kwargs["password"])
        tool.close()
        return r
    else:
        tool.close()
        return "error: illegal func"


if __name__=="__main__":
    dir="example.pdf"
    func="decrypt"
    up="123456"
    op="456789"
    pdfproc("test",func,password=op)