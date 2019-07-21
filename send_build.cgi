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
my $sender_name = ($in{'sender_name'} ne '') ? $in{'sender_name'} : $config{'trans_name'};
my $email = ($in{'e'} ne '') ? $in{'e'} : $config{'trans_team_email'};
my $email_print = '';
my $suffix = '';
my $size = 0;
my $size_print = 0;
my $file = &trans_get_translation_filename (\@array_app, $lang);
my $hid_mods = '';
my $error = '';

$email = ($email eq '') ? 'translations@webmin.com' : $email;
$email_print = &html_escape ($email);

##### POST actions #####
#
# send the file to the browser
if ($in{'download'} ne '')
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

# send the email
if ($in{'send'} ne '')
{
  my ($res, $msg) = &trans_archive_send ($config{'trans_email'},
      $email, $sender_name, $body, $file, \@array_app, $lang);
      
  if ($res)
  {
    print "Location: /$module_name/admin_main.cgi?o=sent_archive\n\n";
    exit;
  }
  else
    {$error = "<p><b>$text{'MSG_SEND_EMAIL_ERROR'}:</b> <code>$msg</code></p>";}
}

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'SEND_TITLE'}</h1>), $app;
print qq(<p>$text{'SEND_BUILD_DESCRIPTION'}</p>);

&trans_send_check_config ();
print $error;
  
print qq(<p>);
print qq(<form action="send_build.cgi" method="post">);
print qq(<input type="hidden" name="e" value="$email">);

foreach my $mod (@array_app) {$hid_mods .= "$mod|"}
$hid_mods =~ s/\|$//g;
print qq(<input type="hidden" name="app" value="$in{'app'}">);
print qq(<input type="hidden" name="a" value="$hid_mods">);
  
print qq(<input type="hidden" name="l" value="$lang">);
printf qq(
  <p>
  <table border=1>
  <tr><td $cb>$text{'SENDER_NAME'}:</td><td><input size="60" type="text" name="sender_name" value="%s"></td></tr>
  <tr><td $cb>$text{'RECIPIENT'}:</td><td>$email_print</td></tr>
  <tr><td $cb>$text{'FILENAME'}:</td><td>$file</td></tr>
  <tr><td $cb>$text{'FILESIZE'}:</td><td>$size_print</td></tr>
  <tr><td $cb colspan="2" align="center"><b>$text{'EMAIL_BODY'}</b></td></tr>
  <tr><td colspan="2" align="center"><textarea name="body" rows="10" cols="80">%s</textarea></td></tr>
  <tr><td colspan="2" align="center">
  <input type="submit" value="$text{'SEND'}" name="send">
  <input type="submit" value="$text{'DOWNLOAD'}" name="download">
  </td></tr>
  <tr><th $cb colspan="2">$text{'ARCHIVE_CONTENT'}</th></tr>
  <tr><td colspan="2">), &html_escape ($sender_name), &html_escape ($body);

  &trans_archive_list_content ($file);

  print qq(</td></tr>
  </table>
  </p>
  );

print qq(</form>);
print qq(</p>);

print qq(<hr>);

my $url = 'send_main.cgi?';
$hid_mods = '';
foreach my $mod (@array_app) {$hid_mods .= "$mod\0"}
$hid_mods =~ s/\0$//;
$url .= '&app=' . &urlize ($hid_mods);

&footer($url, $text{'MODULE_INDEX_SEND'});
