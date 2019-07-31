#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my %file = &trans_get_items (&trans_get_path ($app, "config.info.$lang"));
my %file_ref = &trans_get_items (&trans_get_path ($app, 'config.info'));
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);
my %removed = &trans_get_hash_diff_removed ($ref_lang, $lang, \%file_ref, \%file);

&trans_header ($text{'MODULE_CONFIG_VIEW_ADDED_TITLE'}, $app, $lang);
printf (qq(<br/>$text{'MODULE_CONFIG_VIEW_ADDED_DESCRIPTION'}</p>), "config.info.$lang");

print qq(<p>);
print qq(<table class="trans keys-values" width="100%">);
while (my ($k, $v) = each (%new))
{
  printf (qq(<tr><td>$k:</td><td>%s</td></tr>), &html_escape($v));
}
print qq(</table>);
print qq(</p>);

&trans_footer("module_config_main.cgi?app=$app", $text{'MODULE_CONFIG_INDEX'});
