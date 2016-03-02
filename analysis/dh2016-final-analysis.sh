NAME="1M_5min"
SIMILAR="similar_$NAME"
RESULTS="results_$NAME"

if [ $# -ne 1 ]; 
    then echo "Provide path containing model directory"
    exit 1
fi
MODELS=$1/$NAME/model

top=$(python ../python/frequent_words_in_dta.py 10 arnim_wunderhorn0*.tcf.xml | tr " " ";")
echo "Top10: $top"
rm -rf $RESULTS
mkdir $RESULTS

old=""
for x in ${MODELS}1799_1799 ${MODELS}180{0..8}_????
do
	old="${old};$x"
done
old=$(echo ${old/;/})

new=""
for x in ${MODELS}200?_????
do
	new="${new};$x"
done
new=$(echo ${new/;/})

python ../python/similar_words_batch.py $top 3 $old $new > $SIMILAR
cat $SIMILAR
python ../python/changes_over_time_batch.py $SIMILAR $RESULTS ${MODELS}1799_1799 ${MODELS}{18,19,20}??_????
rm $SIMILAR

python ../python/overall_changes_batches.py ${MODELS}1798_1798 ${MODELS}2009_2009 1 > overal_changes_$NAME
for x in $(echo $top | tr ";" " ")
do 
	echo grep "^$x " overal_changes_$NAME
done