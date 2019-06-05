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
my @rows = ();
my %file_ref = ();
my $have_ref = 0;
my @langs = ();
my $monitor = $in{'monitor'};
my $wu = &trans_get_current_app ();
my $config_info_file = ($config{'trans_webmin'} == 1) ?
  'config.info' : 'uconfig.info';

if ($app eq $old_app && defined ($monitor))
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
  # updated translation
  elsif ($in{'o'} eq 'update_trans')
  {
    $ret = sprintf qq(<p><b>$text{'MSG_UPDATED_TRANSLATION'}</b></p>), $in{'t'}
  }
  
  return $ret;
}

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "config", 1, 0);
print "<hr>\n";
printf qq(<h1>$text{'MODULE_CONFIG_TITLE'}</h1>), $app;
&trans_get_menu_icons_panel ('module_config_main', $app);
print qq(<p>$text{'MODULE_CONFIG_DESCRIPTION1'}</p>);

print qq(<p>);
print qq(<form action="module_config_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);
print qq(<select name="app" onChange="submit()">);
printf qq(<option value="">$text{'SELECT_MODULE'}</option>\n);
&trans_modules_list_get_options ([$app], '');
print "</select>";

print qq(<input type="submit" value="$text{'REFRESH'}">);

&trans_monitor_panel ($app) if ($app ne '');

# display state message
print &my_get_msg ();

# if a module have been choosen
if ($app ne '')
{
  my $updated = 0;
  my $path = &trans_get_path () . "/$app";

  # if there is a config.info file
  if (-f "$path/$config_info_file")
  {
    print qq(<p>$text{'MODULE_CONFIG_DESCRIPTION2'}</p>);

    print qq(<p>$text{'FINGERPRINT_DESCRIPTION'}</p>);

    # retrieve all languages for this module
    opendir (DIR, "$path/lang/");
    foreach my $item (readdir (DIR))
    {
      push @langs, ".$item" 
        if &trans_is_language ($item);
    }
    closedir (DIR);
    push @langs, '' if (! -f "$path/$config_info_file.$ref_lang");

    # seach for all translation files for the selected module
    foreach my $item (@langs)
    {
      my %row = ();
      my %file = ();
      my $name = '';
      my $lang = '';
 
      $lang = ($item =~ /^\./) ? 
        substr ($item, 1, length ($item)) : $ref_lang;
	
      next if (! -f "$path/$config_info_file$item") and
        ($ref_lang eq $lang);
        
      if (! -f "$path/$config_info_file$item")
      {
        $row{'file'} = ();
        $row{'count'} = 0;
        $row{'reference'} = 0;
        $row{'language'} = $lang;
        $row{'size'} = 0;
        $row{'modified'} = 0;
      }
      else
      {
        %file = &trans_get_items ("$path/$config_info_file$item");
        ($row{'size'}, $row{'modified'}) = 
	  (stat ("$path/$config_info_file$item"))[7,9];
    
        $row{'file'} = \%file;
        $row{'count'} = scalar (keys (%file));
        $row{'reference'} = ($ref_lang eq $lang) ? 1 : 0;
        $row{'language'} = $lang;
      }
      
        push @rows, \%row;
        if ($row{'reference'} == 1)
        {
          $have_ref = 1;
          %file_ref = %file;
        }
    }
  
    # manage default language choice
    &trans_get_language_reference ($have_ref, @rows, \%file_ref);
  
    # calculate md5 sum for each field's value
    if ($in{'build_md5'} ne '')
    {
      my $path = &trans_get_path ($app, "config.info.$ref_lang");
      $path = &trans_get_path ($app, 'config.info') if (! -f $path);
      &trans_build_cache ('config', $ref_lang, $path, $app);
    }
  
    $updated = &trans_get_updated ('config', $ref_lang, $app, '');
  
    # display translation table for the selected module
    print qq(<p>);
    print qq(<table border="0" cellspacing="2" cellpadding="2">);
    printf qq(
      <tr $tb>
      <th valign="top">$text{'STATE'}</th>
      <th valign="top">$text{'REFERENCE'}</th>
      <th valign="top">$text{'LANGUAGE'}</th>
      <th valign="top">$text{'MODIFIED'}</th>
      <th valign="top">$text{'SIZE'}</th>
      <th valign="top">$text{'ITEMS'}</th>
      <th valign="top">$text{'ADDED_ITEMS'}</th>
      <th valign="top">$text{'REMOVED_FROM'}</th>
      <th valign="top">$text{'ACTION'}</th></tr>), $ref_lang, $ref_lang;

    foreach my $item (sort {$a->{'language'} cmp $b->{'language'}} @rows)
    {
      my $removed = 0;
      my $new = 0;
      my %row = %{$item};
      my %file = %{$row{'file'}};
      my $state_icon = '';
      my $new_icon = '';
      my $new_panel = '';
      my $removed_icon = '';
      my $removed_panel = '';

      $new = 
        &trans_get_diff_new ($ref_lang, $row{'language'}, \%file_ref, \%file);
      $removed = 
        &trans_get_diff_removed ($ref_lang, $row{'language'}, \%file_ref, \%file);
    
      # state icon
      if ($ref_lang ne $row{'language'})
      {
        $state_icon = ($removed == 0 and $new == 0 and $updated == 0) ?
          qq(<img src="images/smiley_ok.png" alt="$text{'GOOD'}" 
	    title="$text{'GOOD'}">) :
          (($row{'count'} > 0) and 
	    ($removed == 0 or $new == 0) and $updated == 0) ?
            qq(<img src="images/smiley_notbad.png" alt="$text{'NOT_SO_BAD'}" 
              title="$text{'NOT_SO_BAD'}">) :
            qq(<img src="images/smiley_bad.png" alt="$text{'BAD'}" 
	      title="$text{'BAD'}">);
      }
    
      # added items icon
      if ($new == 0)
      {
        $new_icon = qq(<img src="images/ok.png" alt="Ok">);
        $new_panel = '&nbsp;';
      }
      else
      {
        $new_icon = 
          qq(<img src="images/bad.png" alt="$text{'BAD'}"> 
	   <font size=1>$new</font>);
        $new_panel = qq(<a href="module_config_view_added.cgi?app=$app&t=$row{'language'}"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_NEW'}" border="0"></a>);
      }
    
      $ref_panel =
        "<input type=\"submit\" name=\"build_md5\" value=\"$text{'FINGERPRINT'}\">";
      if ($updated > 0)
      {
        $ref_panel .=
          "</td></tr><tr><td nowrap><font=1><b>$updated</b> $text{'ITEMS_MODIFIED'}</font>";
      }
    
      # disappeared items
      if ($removed == 0)
      {
        $removed_icon = qq(<img src="images/ok.png" alt="Ok">);
        $removed_panel = '&nbsp;';
      }
      else
      {
        $removed_icon = 
          qq(<img src="images/bad.png" alt="$text{'BAD'}"> 
	    <font size=1>$removed</font>);
        $removed_panel = 
          qq(<a href="module_config_view_removed.cgi?app=$app&t=$row{'language'}"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_REMOVED'}" border=0></a>);
      }
  
      printf qq(
        <tr %s>
        <th valign="top">%s</th>
        <td align="center" valign="top"><table border=0 cellspacing=0 cellpadding=0><tr><td nowrap>%s</td></tr></table></td>
        <td valign="top"><b>%s</b></td>
	<td valign="top">%s</td>
	<td valign="top" nowrap>%s</td>
	<td valign="top">%s</td>
        <td valign="top"><table border="0" width="100%"><tr>
        <td valign="center" nowrap>%s</td><td align="right">%s</td>
        </tr></table></td>
	<td valign="top"><table border="0" width="100%"><tr>
        <td valign="center" nowrap>%s</td><td align="right">%s</td>
        </tr></table></td>
	<td valign="top"><table border="0" width="100%"><tr>
        <td align="center" nowrap><a href="module_config_edit.cgi?app=$app&t=$row{'language'}"><img src="images/edit.png" alt="$text{'EDIT'}" 
          title="$text{'EDIT_TRANSLATION_FILE'}" border=0></a>
        </td></tr></table></td></tr>\n), 
        ($ref_lang eq $row{'language'}) ? ' bgcolor="cornflowerblue"' : 
	  ($row{'modified'}) ? $cb : ' bgcolor="pink"',
        $state_icon,
	($row{'reference'} == 1) ? $ref_panel : '',
        $row{'language'}, 
        ($row{'modified'}) ?
	  strftime ("%Y-%m-%d", localtime ($row{'modified'})) :
	  qq(<i>$text{'NOT_YET_CREATED'}</i>), 
        &trans_get_string_from_size ($row{'size'}), 
        $row{'count'},
        $new_icon,
        $new_panel,
        $removed_icon,
        $removed_panel,
        $row{'language'};
    }
    print qq(</table>);
    print qq(</p>);
  }
  # if there is no config.info file
  else
  {
    print qq(<p><b>$text{'MODULE_CONFIG_NOEXIST'}</b></p>);
  }
}
print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
