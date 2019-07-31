#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $app = $in{'app'};
my $f1 = $in{'f1'}; $f1 =~ s/[^a-z0-9\-_\.]+//gi;
my $f2 = $in{'f2'}; $f2 =~ s/[^a-z0-9\-_\.]+//gi;
my $content = $in{'content'};
my $path = &trans_get_path ($app, 'help');

my @tmp = split (/\./, $f2);
my $lang = ($#tmp == 2) ? $tmp[1] : $tmp[1].'.'.$tmp[2];

$lang ||= $current_lang;

##### POST actions #####
#
# update the help file (create it if it does not exist)
if (defined ($in{'update'}))
{
  if ($content ne '')
  {
    open (H, '>', "$path/$f2");
    print H $content;
    close (H);
    &trans_char2ent ("$path/$f2", 'html');

    chmod (0644, "$path/$f2");

    &redirect ("help_main.cgi?app=$app&o=update_trans&t=$lang");
    exit;
  }
  else
  {
    $_error = $text{'MSG_TRANSLATION_EMPTY_ERROR'};
  }
}
#
########################

&trans_header ($text{'EDIT_TITLE'}, $app, $lang);

print qq(<br/>);
if ($ref ne $lang)
{
  printf qq($text{'EDIT_DESCRIPTION1'}), $f1, $lang;
}
else
{
  printf qq($text{'EDIT_DESCRIPTION2'}), $f1, $lang;
}
print qq(<p/>);

print qq(<form action="help_edit.cgi" method="post">);
print qq(<input type="hidden" name="f1" value="$f1">);
print qq(<input type="hidden" name="f2" value="$f2">);
print qq(<input type="hidden" name="app" value="$app">);

print qq(<table class="trans header" width="100%">);
print qq(<tr><td>$text{'HELP_CONTENT1'}&nbsp;$lang</td></tr>);
print qq(<tr><td><textarea rows=20 class="to-translate">);

# this file is intended to be in english, so no need to
# encode/decode it (our "modified" detection method is based on
# last modified date, so it will break if we write this file here)
open (H, '<', "$path/$f1"); print $_ while (<H>); close (H);
print qq(</textarea></td></tr>);
print qq(</table>);

print qq(<table class="trans header" width="100%">);
print qq(<tr><td>$text{'HELP_CONTENT2'}</td></tr>);
print qq(<tr><td><textarea rows=20 name="content">);
&trans_char2ent ("$path/$f2", 'work');
open (H, '<', "$path/$f2"); print $_ while (<H>); close (H);
&trans_char2ent ("$path/$f2", 'html');
print qq(</textarea></td></tr>);

print qq(</table>);
print qq(<p/><div><button type="submit" name="update" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-check-circle-o"></i> <span>$text{'UPDATE_TRANSLATION_FILE'}</span></button></div>);
print qq(</form>);

&trans_footer ("help_main.cgi?app=$app", $text{'HELP_INDEX'},
               $_success, $_error, $_info);
