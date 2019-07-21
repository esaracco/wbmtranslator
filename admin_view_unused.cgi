#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $search_type = $in{'search_type'};
my %unused = &trans_get_unused ($search_type, $ref_lang, $app);

sub _purge_items ( $ $ $ )
{
  my ($file, $fcontent, $unused) = @_;

  open (H, '>', $file);
  while (my ($k, $v) = each (%$fcontent))
  {
    print H "$k=$v\n" if (!exists ($unused->{$k}));
  }
  close (H);
}

##### POST actions #####
#
# remove unused items
if ($in{'remove'} ne '')
{
  my $path_lang = &trans_get_path ($app);
  my %fcontent;

  # interface
  if ($search_type eq 'interface')
  {
    foreach my $lang (qw(en en.UTF-8))
    {
      if (-s "$path_lang/lang/$lang")
      {
        %fcontent = &trans_get_items ("$path_lang/lang/$lang");
        &_purge_items ("$path_lang/lang/$lang", \%fcontent, \%unused);
      }
    }
  }
  # config
  else
  {
    %fcontent = &trans_get_items ("$path_lang/config.info");
    &_purge_items ("$path_lang/config.info", \%fcontent, \%unused);
  }
  
  &redirect ("$in{'referer'}.cgi?app=$app&o=remove_unused");
  exit;
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";

print qq(<h1>$text{'VIEW_UNUSED_TITLE'}</h1>);
printf qq(<p>$text{'VIEW_UNUSED_DESCRIPTION'}</p>), $app;
print qq(<p><b>$text{'VIEW_UNUSED_WARNING'}</b></p>);

print qq(<p>);
print qq(<form action="admin_view_unused.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="search_type" value="$search_type">);
print qq(<input type="hidden" name="referer" value="$in{'referer'}">);
print qq(<table border=0 cellspacing=2 cellpadding=2>);
foreach my $key (sort keys %unused)
{
  print qq(
    <tr><td $tb colspan=2><b>$key</b> :</td></tr>
    <tr><td $cb>[<b>$ref_lang</b>]</td><td><code>);
  print &html_escape ($unused{"$key"});
  print qq(</code></td></tr>);
}
print qq(</table>);

print qq(<p><input type="submit" name="remove" value="$text{'REMOVED_FROM_TRANSLATION_FILE'}"></p>);
print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("$in{'referer'}.cgi?app=$app", $text{'PREVIOUS'});
