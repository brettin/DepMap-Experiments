# parses the output of the ipynb
# CHOICE	ANSWER	CORRECT CHOICE	CORRECT ANSWER	CELL_LINE_NAME	SCORE
# assumes ($choice, $answer, $correct_choice, $correct_answer, $cell_line_name, $score)
while(<>){
	next if /CHOICE/;
	chomp;
	my ($choice, $answer, $correct_choice, $correct_answer, $cell_line_name, $score) =split/\t/; 
	$c{$correct_answer} = $c{$correct_answer} + $score ;
	$t{$correct_answer} = $t{$correct_answer} + 1 ;
	$num_correct = $num_correct + $score;
	$total = $total + 1;
}

print STDERR "$num_correct responses out of $total\n";

foreach $k (keys %c) {
	print $k, ",", $c{$k}, ",", $t{$k}, ",", $c{$k}/$t{$k} * 100, "\n";
}
