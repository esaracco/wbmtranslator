#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $old_app = $in{'old_app'};
my @rows = ();
my %file_ref = ();
my $have_ref = 0;
my $webmin_lang = $in{'webmin_lang'};
my $monitor = $in{'monitor'};
my $wu = &trans_get_current_app ();

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
    $ret = sprintf qq(<p><b>$text{'MSG_UPDATED_TRANSLATION'}</b></p>), 
      $in{'t'};
  }

  return $ret;
}

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, undef, 1, 0);
print "<hr>\n";

($webmin_lang ne '') ?
  printf qq(<h1>$text{'INTERFACE_SPECIAL_TITLE'}</h1>),
    ($webmin_lang eq 'lang') ? 'lang' : 'webmin/lang' :
  printf qq(<h1>$text{'INTERFACE_TITLE'}</h1>), $app;
&trans_get_menu_icons_panel ('interface_main', $app);
print qq(<p>$text{'INTERFACE_DESCRIPTION1'}</p>);

print qq(<p>);
print qq(<form action="interface_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<select name="app" onChange="submit()">);
printf qq(<option value="">$text{'SELECT_MODULE'}</option>\n);
&trans_modules_list_get_options ([$app], '');
print "</select>";

print qq(<input type="submit" value="$text{'REFRESH'}">);

&trans_monitor_panel ($app) if ($app ne '');

if ($app eq 'webmin')
{
  print qq($text{'WEBMIN_SPECIAL'});

  print "<p>
    <select name=webmin_lang onChange=\"submit()\">
      <option value=webmin_lang" . 
      (($webmin_lang eq 'webmin_lang') ? ' selected="selected"' : '') . 
      ">webmin/lang/</option>
      <option value=lang" .
      (($webmin_lang eq 'lang') ? ' selected="selected"' : '') .
      ">lang/</option>
    </select>
  </p>"
}

# display state message
print &my_get_msg ();

if ($app ne '')
{
  my $basic_webmin = ($app eq 'webmin' and $webmin_lang eq 'lang');
  my $updated = 0;
  my $path = &trans_get_path ($app, 'lang/');
  my $md5_file =  
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/" .
    "fingerprints/\%s-interface_\%s";

  if ($basic_webmin)
  {
    $path = "$root_directory/lang/"
  }
  
  printf qq(<p>$text{'INTERFACE_DESCRIPTION2'}</p>), $module_name, $app;
  
  print qq(<p>$text{'FINGERPRINT_DESCRIPTION'}</p>);
  
  #seach for all translation files for the selected module
  if (opendir (DIR, "$path"))
  {
    foreach my $item (readdir (DIR))
    {
      next if not &trans_is_language ($item);
  
      my %row = ();
      my %file = ();
      my $name = '';
  
      %file = &trans_get_items ("$path/$item");
      ($row{'size'}, $row{'modified'}) = (stat ("$path/$item"))[7,9];
    
      $row{'file'} = \%file;
      $row{'count'} = scalar (keys (%file));
      $row{'reference'} = ($ref_lang eq $item) ? 1 : 0;
      $row{'language'} = $item;
      push @rows, \%row;
  
      if ($row{'reference'} == 1)
      {
        $have_ref = 1;
        %file_ref = %file;
      }
    }
    closedir (DIR);
  
    # manage default language choice
    $ref_lang = 'en' if (!$have_ref);
    &trans_get_language_reference ($have_ref, @rows, \%file_ref);
  
    # calculate md5 sum for each field's value
    if ($in{'build_md5'} ne '')
    {
      &trans_build_cache ('interface', $ref_lang, 
        &trans_get_path ($app, "lang/$ref_lang", $basic_webmin), $app, 
	  $basic_webmin);
    }
        
    $updated = &trans_get_updated ('interface', $ref_lang, $app, $basic_webmin);
  
    # display translation table for the selected module
    print qq(<p>);
    print qq(<table border="0" cellspacing="2" cellpadding="2">);
    print qq(
      <tr $tb>
      <th valign="top">$text{'STATE'}</th>
      <th valign="top">$text{'REFERENCE'}</th>
      <th valign="top">$text{'LANGUAGE'}</th>
      <th valign="top">$text{'MODIFIED'}</th>
      <th valign="top">$text{'SIZE'}</th>
      <th valign="top">$text{'ITEMS'}</th>
      <th valign="top">$text{'ADDED_ITEMS'}</th>
      <th valign="top">$text{'REMOVED_FROM'}</th>
      <th valign="top">$text{'ACTION'}</th>
      </tr>);
    
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
      my $ref_panel = '';
      my $file_panel = '';
  
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
          (($row{'count'} > 0) and ($removed == 0 or $new == 0) 
  	  and $updated == 0) ?
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
        $new_panel = qq(<a href="interface_edit_added.cgi?app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/edit.png" alt="$text{'EDIT'}" title="$text{'TRANSLATE_NEW'}" border="0"></a>);
      }
    
      $ref_panel =
        qq(<input type="submit" name="build_md5" value="$text{'FINGERPRINT'}">);
      $ref_panel .=
        qq(</td></tr><tr><td nowrap><font=1><b>$updated</b> 
          $text{'ITEMS_MODIFIED'}</font>) if ($updated > 0);
    
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
          qq(<a href="interface_view_removed.cgi?referer=interface_main&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_REMOVED'}" border=0></a><a href="interface_view_removed.cgi?referer=interface_main&remove=1&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/delete.png" alt="$text{'DELETE'}" title="$text{'DELETE_REMOVED'}" border=0></a>);
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
        <td align="right">%s%s
        </td></tr></table></td></tr>\n), 
        ($ref_lang eq $row{'language'}) ? ' bgcolor="cornflowerblue"' : $cb,
        $state_icon,
        ($row{'reference'} == 1) ? $ref_panel : '',
        $row{'language'}, 
        strftime ("%Y-%m-%d", localtime ($row{'modified'})), 
        &trans_get_string_from_size ($row{'size'}), 
        $row{'count'},
        $new_icon,
        $new_panel,
        $removed_icon,
        $removed_panel,
        ($row{'count'} > 0) ?
          sprintf qq(<a href="interface_edit.cgi?app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/edit.png" alt="$text{'EDIT'}"
            title="$text{'EDIT_TRANSLATION_FILE'}" border=0></a>), 
  	  $row{'language'} : qq(<img src="images/empty.png">),
        ($ref_lang ne $row{'language'}) ?
          sprintf qq(<a href="remove.cgi?referer=interface_main&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/delete.png" alt="$text{'DELETE'}" 
  	  title="$text{'DELETE_TRANSLATION'}" border=0></a>), 
  	  $row{'language'} : qq(<img src="images/empty.png">)
        ;
    }
    print qq(</table>);
    print qq(</p>);
  }
  else
  {
    print qq(<p><b>$text{'NO_LANGUAGES'}</b></p>);
  }
}

print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
