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
my @langs = ();
my $wu = &trans_get_current_app ();
my $config_info_file = ($config{'trans_webmin'} == 1) ?
  'config.info' : 'uconfig.info';
my $path = &trans_get_path()."/$app";
my $have_config = (-f "$path/$config_info_file");

# init_msg ()
#
# Set success or error message.
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

&trans_header ($text{'MODULE_CONFIG_TITLE'}, $app, $in{'t'});
&trans_get_menu_icons_panel ('module_config_main', $app);
print qq(<br/>$text{'MODULE_CONFIG_DESCRIPTION1'});

print qq(<p>);
print qq(<form action="module_config_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);

&trans_modules_list_get_options ([$app], '');

if ($have_config && (my $msg = &trans_monitor_panel ($app, $in{'monitor'})))
{
  $_success = $msg;
}

# Set success or error msg
&init_msg ();

# if a module have been selected
if ($app ne '')
{
  my $updated = 0;

  # if there is a config.info file
  if ($have_config)
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
  
    #TODO Code factorization (see also "interface_main.cgi")

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
        &trans_get_path ($app, "lang/$ref_lang", 1),
        $app,
        1
      );
      &trans_build_cache (
        'config',
        $ref_lang,
        &trans_get_path ($app, 'config.info', 1),
        $app,
        1
      );

      $_success = sprintf ($text{'MSG_FINGERPRINT_DONE'}, $ref_lang);
    }
  
    $updated = &trans_get_updated ('config', $ref_lang, $app, '');

    $ref_panel =
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
        $new_panel = qq(<a href="module_config_view_added.cgi?app=$app&t=$row{'language'}"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_NEW'}"></a>);
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
          qq(<a href="module_config_view_removed.cgi?app=$app&t=$row{'language'}"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_REMOVED'}"></a>);
      }
  
      printf qq(
        <tr%s>
        <td align=center>%s</td>
        <td align="center" nowrap>%s</td>
        <td><b>%s</b></td>
	<td align=center>%s</td>
	<td nowrap>%s</td>
	<td>%s</td>
        <td valign=center nowrap>%s %s</td>
	<td valign=center nowrap>%s %s</td>
	<td align=center nowrap><a href="module_config_edit.cgi?app=$app&t=$row{'language'}"><img src="images/edit.png" alt="$text{'EDIT'}" 
          title="$text{'EDIT_TRANSLATION_FILE'}"></a>
        </td></tr>),
        ($ref_lang eq $row{'language'}) ? ' class="selected"' : 
	  ($row{'modified'}) ? '' : ' class="modified"',
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
    $_error = $text{'MODULE_CONFIG_NOEXIST'};
  }
}
print qq(</form>);
print qq(</p>);

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
