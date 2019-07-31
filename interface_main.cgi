#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $app = $in{'app'};
my $old_app = $in{'old_app'};
my @rows = ();
my %file_ref = ();
my $have_ref = 0;
my $webmin_lang = $in{'webmin_lang'};
my $wu = &trans_get_current_app ();
my $basic_webmin = ($app eq 'webmin' && (!$webmin_lang || $webmin_lang eq 'lang'));

# init_msg ()
#
# set success or error message.
#
sub init_msg ()
{
  # creation of the new translation was ok
  if ($in{'o'} eq 'new_trans')
  {
    $_success = sprintf ($text{'MSG_NEW_TRANSLATION'}, $in{'t'});
  }
  # translation already exists
  elsif ($in{'o'} eq 'new_trans_exist')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_EXIST'}, $in{'t'}, $app);
  }
  # added new items from ref translation to translation
  elsif ($in{'o'} eq 'add_new')
  {
    $_success = sprintf ($text{'MSG_ADDED_ITEMS'}, $in{'t'});
  }
  # added new items from ref translation to translation
  elsif ($in{'o'} eq 'add_new_none')
  {
    $_error = sprintf ($text{'MSG_ADDED_ITEMS_NONE'}, $in{'t'});
  }
  # removed items that do not exists in the ref translation
  elsif ($in{'o'} eq 'remove')
  {
    $_success = sprintf ($text{'MSG_REMOVED_ITEMS'}, $in{'t'});
  }
  # removed all this translation
  elsif ($in{'o'} eq 'remove_trans')
  {
    $_success = sprintf ($text{'MSG_REMOVED_TRANSLATION'}, $in{'t'}, $app);
  }
  # updated translation
  elsif ($in{'o'} eq 'update_trans')
  {
    $_success = sprintf ($text{'MSG_UPDATED_TRANSLATION'}, $in{'t'});
  }
}

&trans_header (($webmin_lang ne '') ?
  sprintf ($text{'INTERFACE_SPECIAL_TITLE'},
    ($webmin_lang eq 'lang') ? 'lang' : 'webmin/lang') :
    $text{'INTERFACE_TITLE'}, $app, $in{'t'});
&trans_get_menu_icons_panel ('interface_main', $app);
print qq(<br>$text{'INTERFACE_DESCRIPTION1'});

print qq(<p>);
print qq(<form action="interface_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);

&trans_modules_list_get_options ([$app], '');

if (my $msg = &trans_monitor_panel ($app, $in{'monitor'}, $basic_webmin))
{
  $_success = $msg;
}

if ($app eq 'webmin')
{
  print qq($text{'WEBMIN_SPECIAL'});

  print "<p>
    <select name=webmin_lang onChange=\"submit()\">
      <option value=lang" .
      (($webmin_lang eq 'lang') ? ' selected="selected"' : '') .
      ">lang/</option>
      <option value=webmin_lang" . 
      (($webmin_lang eq 'webmin_lang') ? ' selected="selected"' : '') . 
      ">webmin/lang/</option>
    </select>
  </p>"
}

# Set success or error msg
&init_msg ();

if ($app ne '')
{
  my $updated = 0;
  my $path = &trans_get_path ($app, 'lang/');

  if ($basic_webmin)
  {
    $path = "$root_directory/lang/"
  }
  
  printf qq(<p>$text{'INTERFACE_DESCRIPTION2'}</p>), $module_name, $app;
  
  print qq(<p>$text{'FINGERPRINT_DESCRIPTION'}</p>);
  
  #seach for all translation files for the selected module
  if (opendir (DIR, $path))
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
  
    #TODO Code factorization (see also "module_config_main.cgi")

    ##FIXME useful ?
    # manage default language choice
    ##$ref_lang = 'en' if (!$have_ref);
    ##&trans_get_language_reference ($have_ref, @rows, \%file_ref);
  
    # calculate md5 sum for each field's value
    if (defined ($in{'build_md5'}))
    {
      &trans_build_cache (
        'interface',
        $ref_lang,
        &trans_get_path ($app, "lang/$ref_lang", $basic_webmin),
        $app, 
	$basic_webmin
      );
      &trans_build_cache (
        'config',
        $ref_lang,
        &trans_get_path ($app, 'config.info', $basic_webmin),
        $app,
        $basic_webmin
      );

      $_success = sprintf ($text{'MSG_FINGERPRINT_DONE'}, $ref_lang);
    }
        
    $updated = &trans_get_updated ('interface', $ref_lang, $app, $basic_webmin);

    my $ref_panel =
      sprintf(qq(<button type="submit" name="build_md5" class="btn btn-%s" title="$text{'BUILD_FINGERPRINT'}"><i class="fa fa-fw fa-bolt"></i> <span>$text{'FINGERPRINT'}</span></button>), ($updated) ? 'warning' : 'success');

    if ($updated)
    {
      $ref_panel .= "<br/><b>$updated</b> $text{'ITEMS_MODIFIED'}";

      $_error = sprintf (qq(<br/>$text{'MSG_ITEMS_MODIFIED_ALERT'}),
                  $updated, $ref_lang);
    }

    # display translation table for the selected module
    print qq(<p>);
    print qq(<table class="trans header" width="100%">);
    print qq(
      <tr>
      <td>$text{'STATE'}</td>
      <td>$text{'REFERENCE'}</td>
      <td>$text{'LANGUAGE'}</td>
      <td>$text{'MODIFIED'}</td>
      <td>$text{'SIZE'}</td>
      <td>$text{'ITEMS'}</td>
      <td>$text{'ADDED_ITEMS'}</td>
      <td>$text{'REMOVED_FROM'}</td>
      <td>$text{'ACTION'}</td>
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
  
      $new = 
        &trans_get_diff_new ($ref_lang, $row{'language'}, \%file_ref, \%file);
      $removed = 
        &trans_get_diff_removed ($ref_lang, $row{'language'}, \%file_ref, \%file);
    
      # state icon
      if ($ref_lang ne $row{'language'})
      {
        $state_icon = ($removed == 0 && $new == 0 && $updated == 0) ?
          qq(<img src="images/smiley_ok.png" alt="$text{'GOOD'}" 
            title="$text{'GOOD'}">) :
          (($row{'count'} > 0) &&
            ($removed == 0 || $new == 0) && $updated == 0) ?
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
        $new_panel = qq(<a href="interface_edit_added.cgi?app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/edit.png" alt="$text{'EDIT'}" title="$text{'TRANSLATE_NEW'}"></a>);
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
          qq(<a href="interface_view_removed.cgi?referer=interface_main&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_REMOVED'}"></a><a href="interface_view_removed.cgi?referer=interface_main&remove=1&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang"><img src="images/delete.png" alt="$text{'DELETE'}" title="$text{'DELETE_REMOVED'}"></a>);
      }
  
      printf qq(
        <tr%s>
        <td align=center>%s</td>
        <td align=center>%s</td>
        <td><b>%s</b></td>
        <td align=center>%s</td>
        <td nowrap>%s</td>
        <td>%s</td>
        <td nowrap>%s %s</td>
        <td nowrap>%s %s</td>
        <td nowrap>%s%s</td></tr>\n), 
        ($ref_lang eq $row{'language'}) ? ' class="selected"' :
          ($row{'modified'}) ? '' : ' class="modified"',
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
            title="$text{'EDIT_TRANSLATION_FILE'}"></a>), 
  	  $row{'language'} : qq(<img src="images/empty.png">),
        ($ref_lang ne $row{'language'}) ?
          sprintf qq(<a href="remove.cgi?referer=interface_main&app=$app&t=$row{'language'}&webmin_lang=$webmin_lang&c=lang"><img src="images/delete.png" alt="$text{'DELETE'}" 
  	  title="$text{'DELETE_TRANSLATION'}"></a>), 
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

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
