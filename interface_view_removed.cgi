#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my $webmin_lang = $in{'webmin_lang'};
my %removed = ();
my %file_ref = ($webmin_lang eq 'lang') ?
  &trans_get_items ("$root_directory/lang/$ref_lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$ref_lang"));
my %file = ($webmin_lang eq 'lang') ?
  &trans_get_items ("$root_directory/lang/$lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$lang"));
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);

##### POST actions #####
#
# delete removed items
if ($in{'remove'} ne '')
{
  ($webmin_lang eq 'lang') ?
    open (H, ">$root_directory/lang/$lang") :
    open (H, ">" . (&trans_get_path ($app, "lang/$lang")));
  foreach my $item (keys %file)
  {
    my $found = 0;

    foreach my $i (keys %removed)
    {
      if ($file{$item} eq $removed{$i})
        {$found = 1; next;}
    }

    print H "$item=$file{$item}\n" if (!$found);
  }
  close (H);

  ($webmin_lang eq 'lang') ?
    &trans_char2ent ("$root_directory/lang/$lang", 'html') :
    &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');
  
  &redirect ("$in{'referer'}.cgi?app=$app&t=$lang&o=remove&webmin_lang=$webmin_lang");
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";

printf qq(<h1>$text{'VIEW_REMOVED_TITLE'}</h1>), $app;
printf qq(<p>$text{'VIEW_REMOVED_DESCRIPTION'}</p>), $ref_lang, $lang;

print qq(<p>);
print qq(<form action="interface_view_removed.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);
print qq(<input type="hidden" name="referer" value="$in{'referer'}">);
print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (sort keys %removed)
{
  print qq(
    <tr><td $tb colspan=2><b>$key</b> :</td></tr>
    <tr><td $cb>[<b>$lang</b>]</td><td><code>);
  print &html_escape ($removed{"$key"});
  print qq(</code></td></tr>);
}
print qq(</table>);

print qq(<p><input type="submit" name="remove" value="$text{'REMOVED_FROM_TRANSLATION_FILE'}"></p>);
print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("$in{'referer'}.cgi?app=$app&webmin_lang=$webmin_lang", $text{'PREVIOUS'});
