#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $lang = $in{'l'};
my @array_app = split(/\|/, $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $body = $in{'body'};
my $suffix = '';
my $size = 0;
my $size_print = 0;
my $webmin_version = &get_webmin_version();
my $module_version = ($multiple_modules) ? '' : &trans_get_module_version ($app);
my $file = &trans_get_translation_filename (\@array_app, $lang);
my $filename = $file;
my $hid_mods = '';

##### POST actions #####
#
# send the file to the browser
if (defined ($in{'download'}))
{
  &trans_archive_send_browser ($file);
  exit;
}
# create the file
elsif (!$in{'send'})
{
  &trans_archive_create ($file, $lang, \@array_app);
}
#
########################

$size = -s "/$config{'trans_working_path'}/.translator/$remote_user/archives/$file";
$size_print = &trans_get_string_from_size ($size);

&trans_header ($text{'ARCHIVE_TITLE'}, $app, $lang);

print qq(<p>);
print qq(<form action="archive_build.cgi" method="post">);

foreach my $mod (@array_app) {$hid_mods .= "$mod|"}
$hid_mods =~ s/\|$//g;
print qq(<input type="hidden" name="app" value="$in{'app'}">);
  
print qq(<input type="hidden" name="l" value="$lang">);
print qq(
  <p>
  <table class="trans keys-values" width="100%">
  <tr><td>$text{'FILENAME'}:</td><td>$filename</td></tr>
  <tr><td>$text{'FILESIZE'}:</td><td>$size_print</td></tr>
  </table>

  <p/><div><button type="submit" class="btn btn-success" name="download"><i class="fa fa-fw fa-download"></i> <span>$text{'DOWNLOAD'}</span></button></div>

  <p/><table class="trans header" width="100%">
  <tr><td>$text{'ARCHIVE_CONTENT'}</td></tr>
  <tr><td>);
  &trans_archive_list_content ($file);
  print qq(</td></tr>
  </table>
  </p>
);

print qq(</form>);
print qq(</p>);

&trans_footer("admin_main.cgi?app=".(($multiple_modules)?'':$app), $text{'MODULE_ADMIN_INDEX'});
