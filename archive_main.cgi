#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $module_type = ($in{'module_type'}) ? $in{'module_type'} : 'core';
my $old_module_type = $in{'old_module_type'}||'';
my @array_app = my @array_app = ($module_type ne $old_module_type) ? () : split(/\0/, $in{'app'});
push (@array_app, $in{'app'}) if (!scalar (@array_app) && $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $lang = $in{'lang'};
if (not $in{'module_type'} and $app and not $multiple_modules)
  {$module_type = (&trans_is_webmin_module ($app)) ? 'core' : 'non-core'}

# my_get_msg ()
# IN: -
# OUT: the message to display or ''
#
# return a state message if a action occured
#
sub my_get_msg ()
{
  my $ret = '';

  if ($in{'create'})
  {
    if ($app eq '')
      {$ret = qq(<p><b>$text{'MSG_ERROR_CHOOSE_MODULE'}</b></p>)}
  }

  return $ret;
}

##### POST actions #####
#
# send email with archive attached
if ($in{'create'} and $app ne '')
{
    my $url = '';
    
    $url = 'archive_build.cgi?l=' . &urlize ($lang) . 
      '&app=';
    foreach my $mod (@array_app)
      {$url .= &urlize ($mod) . "|"};
    $url =~ s/\|$//;
    &redirect ($url);
    exit;
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "send", 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'ARCHIVE_TITLE'}</h1>), $app;
if ($multiple_modules) {&trans_get_menu_icons_panel ('send_main')}
  else {&trans_get_menu_icons_panel ('send_main', $app)}
print qq(<p>$text{'SEND_DESCRIPTION1'}</p>);

# display state message
print &my_get_msg ();

print qq(<p>);
print qq(<form action="archive_main.cgi" method="post">);
print qq(<input type="hidden" name="old_module_type" value="$module_type">);

# radio for choosing to display "core" or "non-core" modules
print qq(<p>$text{'CHOOSE_MODULES_TYPE'}:</p>);
print "<p><input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" name=\"module_type\" id=\"module_type_c\" value=\"core\"" . 
  (($module_type eq 'core') ? ' checked="checked"' : '') . "> <label for=\"module_type_c\">$text{'CORE_MODULES'}</label>";
print "<input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" name=\"module_type\" id=\"module_type_nc\" value=\"non-core\"" . 
  (($module_type eq 'non-core') ? ' checked="checked"' : '') . "> <label for=\"module_type_nc\">$text{'NON_CORE_MODULES'}</label></p>";

# combo of the modules
print qq(<select name="app" id="app" multiple size="10">);
&trans_modules_list_get_options (\@array_app, $module_type);
print "</select>";

print qq(<p><input type="submit" name="refresh" value="$text{'REFRESH_FILTER_LANGUAGES'}"></p>);

if (scalar (@array_app))
{
  print qq(<p>$text{'ARCHIVE_DESCRIPTION2'}</p>);
  
  print qq(<p><select name="lang">);
  printf qq(<option value="">$text{'ALL_LANGUAGES'}</option>\n);
  foreach my $m (&trans_get_existing_translations (\@array_app))
    {print qq(<option value="$m">$m</option>\n);}
  print "</select></p>";
  
  print qq(
    <p>
    <input type="submit" value="$text{'CREATE_ARCHIVE'}" name="create">
    </p>
  );
}

print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
