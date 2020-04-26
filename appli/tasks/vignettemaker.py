from PIL import Image,ImageDraw,ImageFont
import numpy as np,configparser,io,os

def MakeVignette(InFilestr:str,OutFilestr:str,cfg:configparser):
    imgpil = Image.open(InFilestr)
    imgnp = np.array(imgpil)
    section=cfg['vignette']
    gamma=float(section['gamma'])
    scale=float(section['scale'])
    fontheight_px=int(section['fontheight_px'])
    scalebarsize_mm=float(section['scalebarsize_mm'])
    pixel_size=float(section['Pixel_Size'])
    scalebarsize_px = int(round(scalebarsize_mm * 1000 / pixel_size, 0)*scale)
    minimgwidth=scalebarsize_px+10
    fontcolor=section['fontcolor']
    bgcolor="black" if fontcolor=="white" else 254 # 254 comme blanc mais facile à détecter par algo
    if gamma!=1:
        imgnp = np.power((imgnp / 255) , (1 / gamma)) * 255
        imgnp=imgnp.astype(np.uint8)
    if section['invert'].upper()=="Y": # inversion d'image
        imgnp=255-imgnp
    imgpil = Image.fromarray(imgnp) # Transformation du tableau en image PIL une fois les calcules numerique faits
    if scale!=1:
        imgpil=imgpil.resize((int(imgpil.size[0]*scale),int(imgpil.size[1]*scale)),Image.BICUBIC)
    # generation du bandeau d'echelle en bas de l'image
    oldimg=imgpil
    imgpil=Image.new(oldimg.mode,(max([imgpil.size[0],minimgwidth]),imgpil.size[1]+int(section['footerheight_px'])),bgcolor  ) # Nouvelle image plus grande
    imgpil.paste(oldimg) # on y colle l'image en haut
    H=imgpil.size[1]
    draw = ImageDraw.Draw(imgpil)
    LinePoints=[(9, H-4),(9+int(round(scalebarsize_px)), H-4)]
    LinePoints.insert(0,(LinePoints[0][0],LinePoints[0][1]+2))
    LinePoints.append( (LinePoints[2][0], LinePoints[2][1] + 2))
    # print(LinePoints)
    draw.line(LinePoints , fill=fontcolor)
    # draw.line(LinePoints[1:2] , fill=fontcolor)
    # fnt=draw.getfont()
    fichierfonte=os.path.dirname(os.path.realpath(__file__))+'/../static/fonts/source-sans-pro-v9-latin-300.ttf'
    fnt = ImageFont.truetype(fichierfonte, int(round(fontheight_px*1.5)))
    draw.text((10, H-10-fontheight_px), "%g mm"%scalebarsize_mm, fill=fontcolor,font=fnt)

    # imgpil =imgpil.transform((imgpil.size[0],imgpil.size[1]+200),Image.EXTENT,(0,0,imgpil.size[0],imgpil.size[1]),fill=1,fillcolor='red')
    # imgpil.save(dir+'\\testgamma_%s_%d.png'%(imgname,g))
    imgpil.save(OutFilestr)
    #imgpil.show()



if __name__ == "__main__":
    ConfigFile = "compute_vignette.txt"
    dir = R'D:\dev\_client\Lov\UVPApp\TestData\uvp6_sn008_20190430_nke_float_up\ecodata\TestSample1'
    imgname = '20190430-142010_2_biggest.png'
    # imgname = '20190430-150649_1_small.png'
    # imgname='20190430-141541_2_biggest2.png'
    origimg = dir + '\\' + imgname
    ini = configparser.ConfigParser()
    ini.read(R'D:\dev\_client\Lov\UVPApp\TestData\uvp6_sn008_20190430_nke_float_up\ecodata\TestSample1\compute_vignette.txt')

    MakeVignette(dir + '\\' + imgname,dir + '\\test.png' ,ini)