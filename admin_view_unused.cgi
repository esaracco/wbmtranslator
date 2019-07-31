#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
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
if (defined ($in{'remove'}))
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

&trans_header ($text{'VIEW_UNUSED_TITLE'}, $app);
printf (qq(<br/>$text{'VIEW_UNUSED_DESCRIPTION'}), $app);

$_info = $text{'VIEW_UNUSED_WARNING'};

print qq(<p>);
print qq(<form action="admin_view_unused.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="search_type" value="$search_type">);
print qq(<input type="hidden" name="referer" value="$in{'referer'}">);
print qq(<table class="trans keys-values">);
foreach my $key (sort keys %unused)
{
  print qq(
    <tr><td>$key:</td><td>);
  print &html_escape ($unused{"$key"});
  print qq(</td></tr>);
}
print qq(</table>);

print qq(<p/><div><button type="submit" class="btn btn-danger ui_form_end_submit" name="remove"><i class="fa fa-fw fa-trash"></i> <span>$text{'REMOVED_FROM_TRANSLATION_FILE'}</span></button></div>);
print qq(</form>);
print qq(</p>);

&trans_footer("$in{'referer'}.cgi?app=$app", $text{'PREVIOUS'}, $_success, $_error, $_info);
