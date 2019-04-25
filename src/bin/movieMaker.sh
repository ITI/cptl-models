DIR=$1
for file in `ls $DIR/*.eps`
do
    fileName=`echo $file | cut -d '.' -f1`
    echo "convert -density 300 -colorspace sRGB -background transparent $file -resize 1064x1064 $fileName.png"
    convert -density 300 -colorspace sRGB -background "#FFFFFF" -flatten $file -resize 1064x1064 $fileName.png
done
	    
ffmpeg -r 1 -pattern_type glob -i "$DIR/*.png" -c:v libx264 -pix_fmt yuv420p -r 25 output_file.mp4
