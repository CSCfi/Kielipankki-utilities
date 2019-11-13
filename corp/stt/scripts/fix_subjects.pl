#!/bin/perl
#use encoding "utf8";

#--------------------------------------------------
# Fix subjects and remove duplicates for STT
#--------------------------------------------------
#
#



for my $line (<>) {
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level1="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level1=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level2="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level2=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level3="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level3=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_codes="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_codes=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level1_codes="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level1_codes=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level2_codes="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level2_codes=)("\|.*?\|")/$1"$new_value"/;
    }
    if ($line =~ /^<text/) {
	($attr_values) = ($line =~ / subjects_level3_codes="\|(.*?)\|"/);
	@values = split(/\|/, $attr_values);
	%seen = ();
	@unique = grep { ! $seen{ $_ }++ } @values;
	$new_value = "|" . join("|", @unique) . "|";
	$line =~ s/( subjects_level3_codes=)("\|.*?\|")/$1"$new_value"/;
    }

    #remove root element
    $line =~ s/<(\/)?articles>//g;

    print $line;
    
}



   
    


