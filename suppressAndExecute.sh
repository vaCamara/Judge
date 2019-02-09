#lance le programme cree par le make (penser faire le make avant)
#dans cette version, on rentre le nom de l'image complet (avec extension)
#puis les paramatres. Decommenter si vous voulez changez d'autres parametres.
#il utilise 0.5 comme threshold dilatation et 0.02 comme threshold small regions.
#ca marche bien avec 0.2 et 0.02 aussi


echo Enter name of image \(min square, max square,\) threshold dilatation, threshold small regions, sigma = 100

read imageName
#read min
#read max
read dilatation
read smallRegions

#on supprime le dossier cree a l'iteration precedante, sinon j'ai l'impression  que l'algo ne reecrit pas dessus
#si l'image est dans un dossier qui a comme nom le numero de l'image, le dossier de sorti s'appelle output_imageNumber donc decommenter la li$
rm -r output_ #$imageName

./insect_detection.exe $imageName 1700 17000 1 $dilatation $smallRegions 100



#if in old data
#utiliser si l'image est dans un dossier ayant pour nom le numero de l'image.
#./insect_detection.exe /usr/local/src/fichiersClients/BIC_2019/raspberry/$imageName/$imageName.png 1700 17000 1 $dilatation $smallRegions 100


