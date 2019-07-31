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
if (defined ($in{'remove'}))
{
  ($webmin_lang eq 'lang') ?
    open (H, '>', "$root_directory/lang/$lang") :
    open (H, '>', &trans_get_path ($app, "lang/$lang"));

  while (my ($k, $v) = each (%file))
  {
    print H "$k=$v\n" if (!exists ($removed{$k}));
  }

  close (H);

  ($webmin_lang eq 'lang') ?
    &trans_char2ent ("$root_directory/lang/$lang", 'html') :
    &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');

  &redirect ("$in{'referer'}.cgi?app=$app&t=$lang&o=remove&webmin_lang=$webmin_lang");
}
#
########################

&trans_header ($text{'VIEW_REMOVED_TITLE'}, $app, $lang);
printf (qq(<br/>$text{'VIEW_REMOVED_DESCRIPTION'}), $ref_lang, $lang);

print qq(<p>);
print qq(<form action="interface_view_removed.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);
print qq(<input type="hidden" name="referer" value="$in{'referer'}">);
print qq(<table class="trans keys-values" width="100%">);
foreach my $key (sort keys %removed)
{
  print qq(<tr><td>$key:</td><td>);
  print &html_escape ($removed{"$key"});
  print qq(</td></tr>);
}
print qq(</table>);

print qq(<p/><div><button type="submit" name="remove" class="btn btn-danger"><i class="fa fa-fw fa-trash"></i> <span>$text{'REMOVED_FROM_TRANSLATION_FILE'}</span></button></div>);
print qq(</form>);
print qq(</p>);

&trans_footer("$in{'referer'}.cgi?app=$app&webmin_lang=$webmin_lang", $text{'PREVIOUS'});
