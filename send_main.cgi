#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $module_type = ($in{'module_type'}) ? $in{'module_type'} : 'core';
my $old_module_type = $in{'old_module_type'}||'';
my @array_app = ($module_type ne $old_module_type) ? () : split(/\0/, $in{'app'});
push (@array_app, $in{'app'}) if (!scalar (@array_app) && $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $lang = $in{'lang'};
my $email = $in{'email'};
##my $do_not_display = $in{'do_not_display'};
my $bad_email = '';
my $not_display = 0;
my $action = (defined($in{'send_email_webmin'}) ||
              defined($in{'send_email_owner'}));

if ($app && !$multiple_modules && !$in{'module_type'})
{
  $module_type = (&trans_is_webmin_module ($app)) ? 'core' : 'non-core';
}

# init_msg ()
#
# Set success or error message.
#
sub init_msg ()
{
  if ($bad_email ne '')
  {
    $_error = sprintf ($text{'MSG_BAD_EMAIL_ERROR'}, $bad_email);
  }
  elsif ($action)
  {
    if ($app eq '')
    {
      $_error = $text{'MSG_ERROR_CHOOSE_MODULE'};
    }
    elsif (defined ($in{'send_email_owner'}) && $email eq '')
    {
      $_error = $text{'MSG_ERROR_ENTER_EMAIL'};
    }
  }
}

##### POST actions #####
#
# send email with archive attached
if ($action && $app ne '')
{
  my $tmp_email = '';
  
  $tmp_email = $in{'email'} if (defined($in{'send_email_owner'}));
  
  # translation team
  if ($tmp_email eq '' && !defined($in{'send_email_owner'}))
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

    $url = 'send_build.cgi?l='.&urlize($lang).'&e='.&urlize($tmp_email).'&app=';
    foreach my $mod (@array_app)
    {
      $url .= &urlize($mod).'|';
    };
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

##if ($do_not_display)
##{
##  open (H, '>',
##    "/$config{'trans_working_path'}/.translator/$remote_user/not_display_flg");
##  close (H);
##}

##$not_display = (-f "/$config{'trans_working_path'}/.translator/$remote_user/not_display_flg");

&trans_header ($text{'SEND_TITLE'}, $app, $lang);
&trans_get_menu_icons_panel ('send_main', ($multiple_modules)?undef:$app);
print qq(<br/>$text{'SEND_DESCRIPTION1'});

# Set success or error msg
&init_msg ();

print qq(<p>);
print qq(<form action="send_main.cgi" method="post">);
print qq(<input type="hidden" name="old_module_type" value="$module_type">);

# radio for choosing to display "core" or "non-core" modules
print qq(<p>$text{'CHOOSE_MODULES_TYPE'}:</p>);
print "<p><input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" id='mt1' name=\"module_type\" value=\"core\"" . 
  (($module_type eq 'core') ? ' checked="checked"' : '') . "> <label for='mt1'> $text{'CORE_MODULES'}</label> ";
print "<input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" id='mt2' name=\"module_type\" value=\"non-core\"" . 
  (($module_type eq 'non-core') ? ' checked="checked"' : '') . "> <label for='mt2'> $text{'NON_CORE_MODULES'}</label></p>";

&trans_modules_list_get_options (\@array_app, $module_type);

if (scalar (@array_app))
{
  if (($module_type eq 'non-core') && !$not_display)
  {
##    $_info = qq($text{'SEND_EMAIL_ALERT1'}<br/><input type="checkbox" name="do_not_display" value="1" onclick="submit()"> $text{'SEND_EMAIL_ALERT2'});
    $_info = $text{'SEND_EMAIL_ALERT1'};
  }
  
  print qq(<p>$text{'SEND_DESCRIPTION2'}</p>);
  
  print qq(<p><select name="lang">);
  printf qq(<option value="">$text{'ALL_LANGUAGES'}</option>);
  foreach my $m (&trans_get_existing_translations (\@array_app))
  {
    print qq(<option value="$m">$m</option>);
  }
  print "</select></p>";
  
  if ($module_type eq 'core')
  {
    print qq(
        <button type="submit" class="btn btn-success btn-tiny" name="send_email_webmin"><i class="fa fa-fw fa-bolt"></i> <span>$text{'BUILD'}</span></button> $text{'SEND_CHOICE1'}.
    );
  }
  
  print qq(
    <p/><button type="submit" class="btn btn-success btn-tiny" name="send_email_owner"><i class="fa fa-fw fa-envelope"></i> <span>$text{'SEND'}</span></button> $text{'SEND_CHOICE2'}: <input type="text" value="$email" name="email">);
  
  print qq(</form>);
  print qq(</p>);
}

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
