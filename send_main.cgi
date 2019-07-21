#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $module_type = ($in{'module_type'}) ? $in{'module_type'} : 'core';
my $old_module_type = $in{'old_module_type'}||'';
my @array_app = ($module_type ne $old_module_type) ? () : split(/\0/, $in{'app'});
push (@array_app, $in{'app'}) if (!scalar (@array_app) && $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $lang = $in{'lang'};
my $email = $in{'email'};
my $do_not_display = $in{'do_not_display'};
my $bad_email = '';
my $not_display = 0;
my $action = (($in{'send_email_webmin'} ne '') || ($in{'send_email_owner'} ne ''));

if ($app && !$multiple_modules && !$in{'module_type'})
{
  $module_type = (&trans_is_webmin_module ($app)) ? 'core' : 'non-core';
}

# my_get_msg ()
# IN: -
# OUT: the message to display or ''
#
# return a state message if a action occured
#
sub my_get_msg ()
{
  my $ret = '';

  if ($bad_email ne '')
  {$ret = sprintf qq(<p><b>$text{'MSG_BAD_EMAIL_ERROR'}</b></p>), $bad_email}
  elsif ($action)
  {
    if ($app eq '')
      {$ret = qq(<p><b>$text{'MSG_ERROR_CHOOSE_MODULE'}</b></p>)}
    elsif ($in{'send_email_owner'} and $email eq '')
      {$ret = qq(<p><b>$text{'MSG_ERROR_ENTER_EMAIL'}</b></p>)}
  }

  return $ret;
}

##### POST actions #####
#
# send email with archive attached
if ($action and $app ne '')
{
  my $tmp_email = '';
  
  $tmp_email = $in{'email'} if ($in{'send_email_owner'} ne '');
  
  # translation team
  if (($tmp_email eq '') and ($in{'send_email_owner'} eq ''))
  {
    $tmp_email = ($config{'trans_team_email'} ne '') ?
      $config{'trans_team_email'} : 'translations@webmin.com';
  }
  # specific address
  else
  {
    $tmp_email = $in{'email'};
  }

  # check email
  $bad_email = $tmp_email;
  $tmp_email = &trans_email_check ($tmp_email);

  # ok
  if ($tmp_email ne '')
  {
    my $url = '';
    
    &trans_set_user_var ("default_email_$app", $tmp_email)
      if ($module_type eq 'non-core');

    $url = 'send_build.cgi?l=' . &urlize ($lang) . 
      '&e=' . &urlize ($tmp_email) . '&app=';
    foreach my $mod (@array_app)
      {$url .= &urlize ($mod) . "|"};
    $url =~ s/\|$//;
    &redirect ($url);
    exit;
  }
}
else
{
  $email = &trans_get_user_var ("default_email_$app");
}
#
########################

if ($do_not_display)
{
  open (H, ">/$config{'trans_working_path'}/.translator/$remote_user/not_display_flg");
  close (H);
}

$not_display = (-f "/$config{'trans_working_path'}/.translator/$remote_user/not_display_flg");

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "send", 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'SEND_TITLE'}</h1>), $app;
if ($multiple_modules) {&trans_get_menu_icons_panel ('send_main')}
  else {&trans_get_menu_icons_panel ('send_main', $app)}
print qq(<p>$text{'SEND_DESCRIPTION1'}</p>);

# display state message
print &my_get_msg ();

print qq(<p>);
print qq(<form action="send_main.cgi" method="post">);
print qq(<input type="hidden" name="old_module_type" value="$module_type">);

# radio for choosing to display "core" or "non-core" modules
print qq(<p>$text{'CHOOSE_MODULES_TYPE'}:</p>);
print "<p><input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" id='mt1' name=\"module_type\" value=\"core\"" . 
  (($module_type eq 'core') ? ' checked="checked"' : '') . "><label for='mt1'> $text{'CORE_MODULES'}</label> ";
print "<input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" id='mt2' name=\"module_type\" value=\"non-core\"" . 
  (($module_type eq 'non-core') ? ' checked="checked"' : '') . "><label for='mt2'> $text{'NON_CORE_MODULES'}</label></p>";

# combo of the modules
print qq(<select name="app" id="app" multiple size="10">);
&trans_modules_list_get_options (\@array_app, $module_type);
print "</select>";

print qq(<p><input type="submit" name="refresh" value="$text{'REFRESH_FILTER_LANGUAGES'}"></p>);

if (scalar (@array_app))
{
  if (($module_type eq 'non-core') && !$not_display)
  {
    print qq(
  <p>
  <table align="center" cellspacing="5" cellpadding="10" width="60%" style="background: silver;font-size: 10px;font-family: Verdana, Arial, Helvetica, sans-serif;color: black;border: 2px red solid;">
  <tr><td>$text{'SEND_EMAIL_ALERT1'}
  <p> <input type="checkbox" name="do_not_display" value="1" onClick="submit()"> $text{'SEND_EMAIL_ALERT2'}.</p>
  </td></tr>
  </table>
  </p>
    );
  }
  
  print qq(<p>$text{'SEND_DESCRIPTION2'}</p>);
  
  print qq(<p><select name="lang">);
  printf qq(<option value="">$text{'ALL_LANGUAGES'}</option>\n);
  foreach my $m (&trans_get_existing_translations (\@array_app))
    {print qq(<option value="$m">$m</option>\n);}
  print "</select></p>";
  
  print "<ul>";

  if ($module_type eq 'core')
  {
    print qq(
        <li><input type="submit" value="$text{'CLICK_HERE'}" name="send_email_webmin"> $text{'SEND_CHOICE1'}</li>
    );
  }
  
  print qq(
    <li><input type="submit" value="$text{'CLICK_HERE'}" name="send_email_owner"> $text{'SEND_CHOICE2'}: <input type="text" value="$email" name="email">.</li>
  );

  print "</ul>";
  
  print qq(</form>);
  print qq(</p>);
}

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
