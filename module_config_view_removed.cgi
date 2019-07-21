#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my %file_ref = &trans_get_items (&trans_get_path ($app, 'config.info'));
my %file = &trans_get_items (&trans_get_path ($app, "config.info.$lang"));
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";

printf qq(<h1>$text{'VIEW_REMOVED_TITLE'}</h1>), $app;
printf qq(<p>$text{'MODULE_CONFIG_VIEW_REMOVED_DESCRIPTION'}</p>),
  "config.info.$lang";

print qq(<p>);
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
print qq(</p>);

print qq(<hr>);
&footer("module_config_main.cgi?app=$app", $text{'MODULE_CONFIG_INDEX'});
