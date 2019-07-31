#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $app = $in{'app'};
my $old_app = $in{'old_app'};
my $lang = ($in{'lang'} eq '') ? $ref_lang : $in{'lang'};
my $search_type = $in{'search_type'};
my $target = $in{'target'};
my $path = &trans_get_path ($app, 'lang/');
my $interface_selected = ($search_type eq 'interface') ? ' selected="selected"' : '';
my $config_selected = ($search_type eq 'config') ? ' selected="selected"' : '';
my $default_tab = $in{'tab'}||'archives';

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
  # no language
  elsif ($in{'o'} eq 'new_trans_bad_no_language')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_BAD_NO_LANGUAGE'}, $in{'t'});
  }

  # language does not exists
  elsif ($in{'o'} eq 'new_trans_bad_not_exists')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_BAD_NOT_EXISTS'}, $in{'t'});
  }
  # new language is not compatible with current
  elsif ($in{'o'} eq 'new_trans_bad_compat')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_BAD_COMPAT'},
                $in{'t'}, $current_lang);
  }
  # problem when created translation
  elsif ($in{'o'} eq 'new_trans_bad')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_BAD'}, $in{'t'}, $app);
  }
  # added new items from ref translation to translation
  elsif ($in{'o'} eq 'add_new')
  {
    $_success = sprintf ($text{'MSG_ADDED_ITEMS'}, $in{'t'});
  }
  # removed items that do not exists in the ref translation
  elsif ($in{'o'} eq 'remove')
  {
    $_success = sprintf (text{'MSG_REMOVED_ITEMS'}, $in{'t'});
  }
  # removed all this translation
  elsif ($in{'o'} eq 'remove_trans')
  {
    $_success = sprintf ($text{'MSG_REMOVED_TRANSLATION'}, $in{'t'}, $app);
  }
  # removed all unused items
  elsif ($in{'o'} eq 'remove_unused')
  {
    $_success = sprintf ($text{'MSG_REMOVED_UNUSED'}, $in{'t'}, $app);
  }
  # remove selected archives
  elsif ($in{'o'} eq 'delete_archives')
  {
    $_success = $text{'MSG_DELETED_SELECTED_FILES'};
  }
  # archive was sent without problem
  elsif ($in{'o'} eq 'sent_archive')
  {
    $_success = $text{'MSG_SEND_EMAIL_OK'};
  }
}

##### POST actions #####
#
# create new translation if requested
if (defined ($in{'new_translation'}))
{
  if (!$in{'new_trans_code'})
  {
    $in{'o'} = 'new_trans_bad_no_language';
  }
  else
  {
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
      my $ret = &trans_create_translation ($in{'new_trans_code'}, $app);
    
      $in{'o'} =
        ($ret == 1) ? 'new_trans_exist' : 
                      ($ret == 2) ? 'new_trans_bad' :
                                    'new_trans';
    }
  }
}
# Remove a translation
elsif (defined ($in{'remove'}))
{
  &redirect ("remove.cgi?referer=admin_main&app=$app&t=$lang&tab=$default_tab&c=".urlize($target));
  exit;
}
else
{
  foreach my $item (keys %in)
  {
    # Download archive
    if ($item =~ /^download_(.*)/)
    {
      &trans_archive_send_browser ($1);
      exit;
    }
    # Delete archive
    elsif ($item =~ /^delete_(.*)/)
    {
      &trans_archive_delete ($1);
      $in{'o'} = 'delete_archives';
    }
  }
}
#
########################

&trans_header ($text{'ADMIN_TITLE'}, $app, $lang);
&trans_get_menu_icons_panel ('admin_main', $app);
print qq(<br/>$text{'ADMIN_DESCRIPTION1'});

print qq(<p/>);
print qq(<form action="admin_main.cgi" method="post">);
print qq(<input type="hidden" name="tab" value="$default_tab">);
print qq(<input type="hidden" name="old_app" value="$app">);

&trans_modules_list_get_options ([$app], '');

if (my $msg = &trans_monitor_panel ($app, $in{'monitor'}))
{
  $_success = $msg;
}

# Set success or error msg
&init_msg ();

# Tabs management
my @tabs = (['archives', $text{'ADMIN_TAB_TITLE_ARCHIVES'}]);
if ($app ne '')
{
  push @tabs, (
    ['create_delete', $text{'ADMIN_TAB_TITLE_CREATE_DELETE'}],
    ['search', $text{'ADMIN_TAB_TITLE_SEARCH'}]);
}
print ui_tabs_start(\@tabs, 'admin', $default_tab);
print ui_tabs_start_tab('admin', 'archives');
&_archives ();
print ui_tabs_end_tab('admin', 'archives');
if ($app ne '')
{
  print ui_tabs_start_tab('admin', 'create_delete');
  &_create_delete ();
  print ui_tabs_end_tab('admin', 'create_delete');

  print ui_tabs_start_tab('admin', 'search');
  &_search ();
  print ui_tabs_end_tab('admin', 'search');
}
print ui_tabs_end();

# Tab 1 "Archives management"
sub _archives ()
{
  print qq(<div>);

  print qq(<p>$text{'ADMIN_DESCRIPTION3'}</p>);

  print qq(<div><button type="button" onclick="location.href='archive_main.cgi?app=$app'" class="btn btn-default btn-tiny"><i class="fa fa-fw fa-plus-square"></i> <span>$text{'CREATE_ARCHIVE'}</span></button></div>);

# read archives directory
opendir (DIR, "/$config{'trans_working_path'}/.translator/$remote_user/archives/");
@dir = readdir (DIR);
closedir (DIR);

if (scalar (@dir) - 2)
{
  print qq(<p><table class="trans header">);
  print qq(<tr><td>$text{'FILENAME'}</td><td>$text{'ACTION'}</td></tr>);
  foreach my $name (sort @dir)
  {
    next if ($name =~ /^\./);
    print qq(<tr><td>$name</td><td><button type="button" class="btn btn-tiny" onclick="location.href='admin_main.cgi?download_$name=1'"><i class="fa fa-fw fa-download"></i> <span>$text{'DOWNLOAD'}</span></button>&nbsp;<input type="checkbox" name="delete_$name" value="on" onchange="updateActionsChecked(this.form,document.getElementById('delete-archive'), 'delete_')"></td></tr>);
  }
  print qq(</table></p>);

  print qq(<div><button type="submit" onclick="document.querySelector('[name=tab]').value='archives'" id="delete-archive" name="action_delete_trans" class="disabled btn btn-danger ui_form_end_submit"><i class="fa fa-fw fa-trash"></i> <span>$text{'DELETE_SELECTED_FILES'}</span></button></div>);
}

  print qq(</div>);
}

# Tab 2 "Create /delete translations"
sub _create_delete ()
{
  print qq(<div>);

  print qq(<p>$text{'ADMIN_DESCRIPTION2'}</p>);
  
  # Create new translation panel
  print qq(<p/><div><button type="submit" onclick="document.querySelector('[name=tab]').value='create_delete'" name="new_translation" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-bolt"></i> <span>$text{'CREATE'}</span></button> $text{'NEW_TRANSLATION'} <input type="text" name="new_trans_code" size="5" value=""/></div>);

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

    # Create remove translation panel 
    printf (qq(<p/><div><button type="submit" onclick="document.querySelector('[name=tab]').value='create_delete'" name="remove" class="btn btn-danger ui_form_end_submit"><i class="fa fa-fw fa-trash"></i> <span>$text{'DELETE'}</span></button> %s $text{'DELETE_TRANSLATION1'}</div>), $target_select, $select);
  }

  print qq(</div>);
}

# Tab 3 "Search for unused items"
sub _search ()
{
  print qq(<div>);

  print qq(<p>$text{'ADMIN_DESCRIPTION_SEARCH'}</p>);

  # Search for unused items panel
  print qq(<button class="btn btn-success ui_form_end_submit" type="submit" onclick="document.querySelector('[name=tab]').value='search'" name="search_unused"><i class="fa fa-fw fa-search"></i> <span>$text{'SEARCH_UNUSED'}</span></button> $text{'IN'} <select name="search_type"><option value="interface"$interface_selected>$text{'WEB_INTERFACE'}</option><option value="config"$config_selected>$text{'MODULE_CONFIGURATION'}</option></select>);

  # if "search for unused items" button clicked
  if (defined($in{'search_unused'}))
  {
    my %tmp = &trans_get_unused ($search_type, $ref_lang, $app);
    my $unused = scalar (keys (%tmp));
    
    $_success = sprintf ($text{'FOUND_UNUSED_ITEMS'}, $unused);
    if ($unused > 0)
    {
      $_success .= qq(&nbsp;<a href="admin_view_unused.cgi?search_type=$search_type&referer=admin_main&app=$app&tab=$default_tab"><img src="images/view.png" alt="$text{'VIEW'}" title="$text{'VIEW_UNUSED'}"></a>);
    }
  }

  print qq(</div>);
}

print qq(</form>);
print qq(</p>);

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
