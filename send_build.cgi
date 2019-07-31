#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
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

$_info = $text{'SEND_BUILD_ALERT_SMTP'};

$email = ($email eq '') ? 'translations@webmin.com' : $email;
$email_print = &html_escape ($email);

##### POST actions #####
#
# send the file to the browser
if (defined ($in{'download'}))
{
  &trans_archive_send_browser ($file);
  exit;
}
# create the file
elsif (!defined ($in{'send'}))
{
  &trans_archive_create ($file, $lang, \@array_app);
}
#
########################

$size = -s "/$config{'trans_working_path'}/.translator/$remote_user/archives/$file";
$size_print = &trans_get_string_from_size ($size);

# send the email
if (defined ($in{'send'}))
{
  my ($res, $msg) = &trans_archive_send ($config{'trans_email'},
      $email, $sender_name, $body, $file, \@array_app, $lang);
      
  if ($res)
  {
    print "Location: admin_main.cgi?o=sent_archive\n\n";
    exit;
  }
  else
  {
    $_error = "$text{'MSG_SEND_EMAIL_ERROR'}: <code>$msg</code>";
  }
}

&trans_header ($text{'SEND_TITLE'}, $app, $lang);
print qq(<br/>$text{'SEND_BUILD_DESCRIPTION'});

&trans_send_check_config ();
  
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
  <table class="trans keys-values" width="100%">
  <tr><td>$text{'SENDER_NAME'}:</td><td><input size="60" type="text" name="sender_name" value="%s"></td></tr>
  <tr><td>$text{'RECIPIENT'}:</td><td>$email_print</td></tr>
  <tr><td>$text{'FILENAME'}:</td><td>$file</td></tr>
  <tr><td>$text{'FILESIZE'}:</td><td>$size_print</td></tr>
  <tr><td>$text{'EMAIL_BODY'}</td><td><textarea name="body" rows=10>%s</textarea></td></tr>
  <tr><td></td><td>
  <button type="submit" name="send" class="btn btn-success"><i class="fa fa-envelope"></i> <span>$text{'SEND'}</span></button>&nbsp;<button type="submit" name="download" class="btn btn-success"><i class="fa fa-download"></i> <span>$text{'DOWNLOAD'}</span></button>
  </td></tr>
  </table>
  <table class="trans header" width="100%">
  <tr><td>$text{'ARCHIVE_CONTENT'}</td></tr>
  <tr><td>), &html_escape ($sender_name), &html_escape ($body);

  &trans_archive_list_content ($file);

  print qq(</td></tr>
  </table>
  </p>
  );

print qq(</form>);
print qq(</p>);

my $url = 'send_main.cgi?';
$hid_mods = '';
foreach my $mod (@array_app) {$hid_mods .= "$mod\0"}
$hid_mods =~ s/\0$//;
$url .= '&app=' . &urlize ($hid_mods);

&trans_footer ($url, $text{'MODULE_INDEX_SEND'}, $_success, $_error, $_info);
