# parses the output of the ipynb
# assumes ($choice, $answer, $correct_choice, $correct_answer, $score)
while(<>){
	next if /CHOICE/;
	chomp;
	my ($choice, $answer, $correct_choice, $correct_answer, $score) =split/\t/; 
	$correct{$correct_answer} = $correct{$correct_answer} + $score;
	$total{$correct_answer} = $total{$correct_answer} + 1;
}

foreach $k (keys %correct) {
	print $k, ",", $correct{$k}, ",", $total{$k}, ",", $correct{$k}/$total{$k} * 100, "\n";
}
