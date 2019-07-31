#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $module_type = ($in{'module_type'}) ? $in{'module_type'} : 'core';
my $old_module_type = $in{'old_module_type'}||'';
my @array_app = my @array_app = ($module_type ne $old_module_type) ? () : split(/\0/, $in{'app'});
push (@array_app, $in{'app'}) if (!scalar (@array_app) && $in{'app'});
my $multiple_modules = (scalar (@array_app) > 1);
my $app = ($multiple_modules) ? $text{'MULTIPLE_MODULES'} : $array_app[0];
my $lang = $in{'lang'};
if (!$in{'module_type'} && $app && !$multiple_modules)
  {$module_type = (&trans_is_webmin_module ($app)) ? 'core' : 'non-core'}

# init_msg ()
#
# Set success or error message.
#
sub init_msg ()
{
  if (defined ($in{'create'}) && $app eq '')
  {
    $_error = $text{'MSG_ERROR_CHOOSE_MODULE'};
  }
}

##### POST actions #####
#
# send email with archive attached
if (defined ($in{'create'}) && $app ne '')
{
    my $url = '';
    
    $url = 'archive_build.cgi?l='.&urlize($lang).'&app=';
    foreach my $mod (@array_app)
    {
      $url .= &urlize($mod).'|';
    };
    $url =~ s/\|$//;
    &redirect ($url);
    exit;
}
#
########################

&trans_header ($text{'ARCHIVE_TITLE'}, $app);
print qq(<br/>$text{'SEND_DESCRIPTION1'});

# Set success or error msg
&init_msg ();

print qq(<p>);
print qq(<form action="archive_main.cgi" method="post">);
print qq(<input type="hidden" name="old_module_type" value="$module_type">);

# radio for choosing to display "core" or "non-core" modules
print qq(<p>$text{'CHOOSE_MODULES_TYPE'}:</p>);
print "<p><input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" name=\"module_type\" id=\"module_type_c\" value=\"core\"" . 
  (($module_type eq 'core') ? ' checked="checked"' : '') . "> <label for=\"module_type_c\">$text{'CORE_MODULES'}</label>";
print "<input onChange=\"getElementById('app').selectedIndex=-1;submit()\" type=\"radio\" name=\"module_type\" id=\"module_type_nc\" value=\"non-core\"" . 
  (($module_type eq 'non-core') ? ' checked="checked"' : '') . "> <label for=\"module_type_nc\">$text{'NON_CORE_MODULES'}</label></p>";

&trans_modules_list_get_options (\@array_app, $module_type);

if (scalar (@array_app))
{
  print qq(<p>$text{'ARCHIVE_DESCRIPTION2'}</p>);
  
  print qq(<p><select name="lang">);
  printf qq(<option value="">$text{'ALL_LANGUAGES'}</option>\n);
  foreach my $m (&trans_get_existing_translations (\@array_app))
    {print qq(<option value="$m">$m</option>\n);}
  print "</select></p>";
  
  print qq(
    <div><button type="submit" class="btn btn-success ui_form_end_submit" name="create"><i class="fa fa-fw fa-bolt"></i> <span>$text{'CREATE_ARCHIVE'}</span></button></div>
  );
}

print qq(</form>);
print qq(</p>);

&trans_footer ("admin_main.cgi?app=$app", $text{'MODULE_ADMIN_INDEX'}, $_success, $_error, $_info);
