#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307, USA.

require './translator-lib.pl';

my $app = $in{'app'};
my $old_app = $in{'old_app'};
my $lang = ($in{'lang'} eq '') ? $ref_lang : $in{'lang'};
my $search_type = $in{'search_type'};
my $target = $in{'target'};
my $dir = ();
my $monitor = $in{'monitor'};

if ($old_app eq $app)
{
  &trans_set_user_var ("monitor_" . &trans_get_current_app () . "_$app",
    $monitor);
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
  
  # creation of the new translation was ok
  if ($in{'o'} eq 'new_trans')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_NEW_TRANSLATION'}</b></p>), $in{'t'};
  }
  # translation already exists
  elsif ($in{'o'} eq 'new_trans_exist')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_NEW_TRANSLATION_EXIST'}</b></p>), 
      $in{'t'}, $app;
  }
  # language does not exists
  elsif ($in{'o'} eq 'new_trans_bad_not_exists')
  {
    $ret =
      sprintf qq(<p><b>$text{'MSG_NEW_TRANSLATION_BAD_NOT_EXISTS'}</b></p>), 
        $in{'t'};
  }
  # new language is not compatible with current
  elsif ($in{'o'} eq 'new_trans_bad_compat')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_NEW_TRANSLATION_BAD_COMPAT'}</b></p>), 
      $in{'t'}, $current_lang;
  }
  # problem when created translation
  elsif ($in{'o'} eq 'new_trans_bad')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_NEW_TRANSLATION_BAD'}</b></p>), 
      $in{'t'}, $app;
  }
  # added new items from ref translation to translation
  elsif ($in{'o'} eq 'add_new')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_ADDED_ITEMS'}</b></p>), $in{'t'};
  }
  # removed items that do not exists in the ref translation
  elsif ($in{'o'} eq 'remove')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_REMOVED_ITEMS'}</b></p>), $in{'t'};
  }
  # removed all this translation
  elsif ($in{'o'} eq 'remove_trans')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_REMOVED_TRANSLATION'}</b></p>), 
      "$in{'t'}", $app;
  }
  # removed all unused items
  elsif ($in{'o'} eq 'remove_unused')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_REMOVED_UNUSED'}</b></p>),
      "$in{'t'}", $app;
  }
  # remove selected archives
  elsif ($in{'o'} eq 'delete_archives')
  {
    $ret = qq(<p><b>$text{'MSG_DELETED_SELECTED_FILES'}</b></p>);
  }
  # archive was sent without problem
  elsif ($in{'o'} eq 'sent_archive')
  {
    $ret = qq(<p><b>$text{'MSG_SEND_EMAIL_OK'}</b></p>);
  }

  return $ret;
}

##### POST actions #####
#
# create new translation if requested
if (($in{'new_translation'} ne '') and ($in{'new_trans_code'} ne ''))
{
  my $ret = 1;
  my $lang_infos = &get_languages_infos ($in{'new_trans_code'});  

  $in{'t'} = $in{'new_trans_code'};

  if (!$lang_infos)
  {
    $in{'o'} = 'new_trans_bad_not_exists';
  }
  elsif (!$lang_infos->{'current_compat'})
  {
    $in{'o'} = 'new_trans_bad_compat';
  }
  else
  {
    $ret = &trans_create_translation ($in{'new_trans_code'}, $app);
  
    $in{'o'} =
      ($ret == 1) ? 'new_trans_exist' : 
                    ($ret == 2) ? 'new_trans_bad' :
                                  'new_trans';
  }
}
# remove a translation
elsif ($in{'remove'} ne '')
{
  &redirect ("remove.cgi?referer=admin_main&app=$app&t=$lang&c=" .
    urlize ($target));
  exit;
}
else
{
  foreach my $item (keys %in)
  {
    # download a archive
    if ($item =~ /^download_(.*)/)
    {
      &trans_archive_send_browser ($1);
      exit;
    }
    # delete this archive
    elsif ($item =~ /^delete_(.*)/)
    {
      &trans_archive_delete ($1);
      $in{'o'} = 'delete_archives';
    }
  }
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "general", 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'ADMIN_TITLE'}</h1>), $app;
&trans_get_menu_icons_panel ('admin_main', $app);

print qq(<p>);
print qq(<form action="admin_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);

print qq(<p>$text{'ADMIN_DESCRIPTION1'}</p>);

print qq(<p><select name="app" onChange="submit()">);
printf qq(<option value="">$text{'SELECT_MODULE'}</option>\n);
&trans_modules_list_get_options ([$app], '');
print "</select>";
print qq(<input type="submit" value="$text{'REFRESH'}"></p>);

&trans_monitor_panel ($app) if ($app ne '');

# display state message
print &my_get_msg ();

# if user has selected a module
if ($app ne '')
{
  my $updated = 0;
  my $path = &trans_get_path ($app, 'lang/');
  my $interface_selected = ($search_type eq 'interface') ? ' selected="selected"' : '';
  my $config_selected = ($search_type eq 'config') ? ' selected="selected"' : '';
  
  print qq(<p>$text{'ADMIN_DESCRIPTION2'}</p>);
  
  print qq(<table border=0 cellpadding=5 cellspacing=0>\n);
  
  # search for unused items panel
  print qq(
    <tr $tb><td><img src="images/search_24x24.png" align="left" border=0><input type="submit" name="search_unused" value="$text{'SEARCH_UNUSED'}"> $text{'IN'} <select name="search_type"><option value="interface"$interface_selected>$text{'WEB_INTERFACE'}</option><option value="config"$config_selected>$text{'MODULE_CONFIGURATION'}</option></select>
    </td>
  );
 
  # if "search for unused items" button clicked
  if ($in{'search_unused'} ne '')
  {
    my %tmp = &trans_get_unused ($search_type, $ref_lang, $app);
    my $unused = scalar (keys (%tmp));
    
    printf qq(<td $cb>$text{'FOUND_UNUSED_ITEMS'}</td>), $unused;
    if ($unused > 0)
    {
      print qq(<td><a href="admin_view_unused.cgi?search_type=$search_type&referer=admin_main&app=$app"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_UNUSED'}" border=0></a></td>);
    }
    else
    {
      print qq(<td>&nbsp;</td>);
    }
  }
  else
  {
    print qq(<td colspan="2">&nbsp;</td>);
  }

  print qq(</tr>);
  print qq(<tr><td colspan="3">&nbsp;</td></tr>);

  # create new translation panel
  print qq(
    <tr $tb><td colspan="3"><input type="submit" name="new_translation" 
      value="$text{'CREATE'}"> $text{'NEW_TRANSLATION'} 
      <input type="text" name="new_trans_code" size="5" value="">
    </td></tr>
  );

  print qq(<tr><td colspan="3">&nbsp;</td></tr>);

  if (my @trans = &trans_get_existing_translations ([$app]))
  {
    my $select = qq(<select name="lang">);
    foreach my $m (sort @trans)
    {
      $select .= qq(<option value="$m">$m</option>\n);
    }
    $select .= qq(</select>);

    my $target_select = qq(
      <select name="target">
        <option value="all">$text{'ALL'}</option>
        <option value="all_webmin">$text{'ALL_WEBMIN_TRANSLATION'}</option>
        <option value="lang">$text{'ONLY_LANG'}</option>
        <option value="module_info">$text{'ONLY_MODULE_INFO'}</option>
        <option value="config_info">$text{'ONLY_CONFIG_INFO'}</option>
        <option value="all_usermin">$text{'ALL_USERMIN_TRANSLATION'}</option>
        <option value="ulang">$text{'ONLY_ULANG'}</option>
        <option value="umodule_info">$text{'ONLY_UMODULE_INFO'}</option>
        <option value="uconfig_info">$text{'ONLY_UCONFIG_INFO'}</option>
      </select>
    );

  # create remove translation panel 
  printf qq(
    <tr $tb><td colspan="3"><input type="submit" name="remove" 
      value="$text{'DELETE'}"> %s $text{'DELETE_TRANSLATION1'}</td></tr>), 
        $target_select, $select;
  }

  print qq(</table>);
}

  print qq(<h2>$text{'ADMIN_TITLE2'}</h2>);

  print qq(<p>$text{'ADMIN_DESCRIPTION3'}</p>);

  print qq(<p><a href="/$module_name/archive_main.cgi?app=$app">$text{'CREATE_ARCHIVE'}</a></p>);

# read archives directory
opendir (DIR, "/$config{'trans_working_path'}/.translator/$remote_user/archives/");
@dir = readdir (DIR);
closedir (DIR);

if (scalar (@dir) - 2)
{
  print qq(<p><table border="1">);
  print qq(<tr $tb><th>$text{'FILENAME'}</th><th>$text{'ACTION'}</th></tr>);
  foreach my $name (sort @dir)
  {
    next if ($name =~ /^\./);
    print qq(<tr $cb><td>$name</td><td><input type="submit" name="download_$name" value="$text{'DOWNLOAD'}">&nbsp;<input type="checkbox" name="delete_$name" value="on"></td></tr>);
  }
  print qq(</table></p>);

  print qq(<p><input type="submit" name="action_delete_trans" value="$text{'DELETE_SELECTED_FILES'}"></p>);
}

print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
