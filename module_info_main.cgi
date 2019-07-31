#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my ($_success, $_error, $_info) = ('', '', '');
my $app = $in{'app'};
my $old_app = $in{'old_app'};
my $path = &trans_get_path ('', '') . "/$app";
my $finfo = (&trans_is_theme ($app)) ? 'theme' : 'module';

# init_msg ()
#
# Set success or error message.
#
sub init_msg ()
{
  # Creation of the new translation was ok
  if ($in{'o'} eq 'new_trans')
  {
    $_success = sprintf ($text{'MSG_NEW_TRANSLATION'}, $in{'t'});
  }
  # Translation already exists
  elsif ($in{'o'} eq 'new_trans_exist')
  {
    $_error = sprintf ($text{'MSG_NEW_TRANSLATION_EXIST'}, $in{'t'}, $app);
  }
  # Added new items from ref translation to translation
  elsif ($in{'o'} eq 'add_new')
  {
    $_success = sprintf ($text{'MSG_ADDED_ITEMS'}, $in{'t'});
  }
  # Updated translation
  elsif ($in{'o'} eq 'update_trans')
  {
    $_success = sprintf ($text{'MSG_UPDATED_TRANSLATION'}, $in{'t'});
  }
}

sub trans_display_description_table ( $ $ $ \@ )
{
  my ($type, $title, $ref_line, $h) = @_;
  my %hash = %$h;

  print qq(<p><table class="trans keys-values" width="100%">);
  print qq(<tr><td>$title</td><td class="to-translate">$ref_line</td></tr>);
  print qq(</table>);

   print qq(<p><table class="trans header keys-values" width="100%">);
  print qq(<tr><td>$text{'LANGUAGE'}</td><td>$text{'DESCRIPTION'}</td></tr>);
  foreach my $key (sort keys %hash)
  {
    next if (!&trans_is_language ($key));
    my $value_print = &html_escape ($hash{$key});
    
    print qq(
      <tr>
      <td>$key</td>
      <td><input type="text" value="$value_print" name="${type}_$key" size="100%"></td></tr>);
  }
  print qq(</table></p>);
}

sub read_file_descs ( $ $ $ $ $ )
{
  my ($f, $ref_line_short, $ref_line_long, $hash_short, $hash_long) = @_;

  open (H, '<', $f);
  while (my $line = <H>)
  {
    next if ($line !~ /^(desc|longdesc)/);
    my ($name, $value) = split (/=/, $line);
    my $value_print = &html_escape ($value);

    if ($name eq 'desc')
    {
      $$ref_line_short = &html_escape ($value);
    }
    elsif ($name eq 'longdesc')
    {
      $$ref_line_long = &html_escape ($value);
    }
    elsif ($name =~ /^desc_(.*)$/)
    {
      $hash_short->{$1} = &trans_ent2char_buffer ($value);
    }
    elsif ($name =~ /^longdesc_(.*)$/)
    {
      $hash_long->{$1} = &trans_ent2char_buffer ($value);
    }
  }
  close (H);
}

##### POST action #####
#
# Update module.info/theme descriptions
if (defined ($in{'update'}))
{
  my %hash_main = ();
  my %hash_extra = ();

  unlink ("$config_directory/$finfo.infos.cache");

  &read_file ("$path/$finfo.info", \%hash_main);

  foreach my $key (keys %in)
  {
    next if ($key !~ /desc_(.*)/);
    my $lang = $1;

    if (&trans_lang_must_be_encoded ($lang))
    {
      $in{$key} = &trans_char2ent_buffer ($in{$key});
    }
    else
    {
      $in{$key} = &trans_ent2char_buffer ($in{$key});
    }

    if (exists ($hash_main{$key}))
    {
      $hash_main{$key} = $in{$key};
    }
    else
    {
      $hash_extra{$lang}{$key} = $in{$key};
    }
  }

  # write main module.info file
  &write_file ("$path/$finfo.info", \%hash_main);

  # write extra module.info file per language if needed
  while (my ($k, $v) = each (%hash_extra))
  {
    &write_file ("$path/$finfo.info.$k", $v);
  }

  $_success = $text{'MSG_MODULE_INFO_UPDATE'};
}
#
########################

&trans_header ($text{'MODULE_INFO_TITLE'}, $app);
&trans_get_menu_icons_panel ('module_info_main', $app);
print qq(<br/>$text{'MODULE_INFO_DESCRIPTION'});

print qq(<p>);
print qq(<form action="module_info_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);

&trans_modules_list_get_options ([$app], '');

if (my $msg = &trans_monitor_panel ($app, $in{'monitor'}))
{
  $_success = $msg;
}

# Set success or error msg
&init_msg ();

# if a module have been chosen
if ($app ne '')
{
  my $updated = 0;
  my %hash_short = ();
  my %hash_long = ();
  my $ref_line_short = '';
  my $ref_line_long = '';
 
  # read in main module.info/theme.info
  &read_file_descs (
    "$path/$finfo.info",
    \$ref_line_short, \$ref_line_long,
    \%hash_short, \%hash_long);

  # read dedicated module.info file per language if some
  if ($finfo eq 'module')
  {
    opendir (DH, "$path/");
    foreach my $item (readdir (DH))
    {
      if ($item =~ /^$finfo.info\./)
      {
        &read_file_descs (
          "$path/$item",
          undef, undef,
          \%hash_short, \%hash_long);

      }
    }
    closedir (DH);
  }

  # Check for missed languages (sometimes there is more languages in lang/ 
  # than in module.info/theme.info)
  opendir (DH, "$path/lang/");
  foreach my $item (readdir (DH))
  {
    if ($item ne $ref_lang && &trans_is_language ($item))
    {
      $hash_short{$item} = '' if (!exists ($hash_short{$item}));
      $hash_long{$item} = '' if (!exists ($hash_long{$item}));
    }
  }
  closedir (DH);

  &trans_display_description_table ('desc', 
                                    $text{'MODULE_CONFIG_SHORT_DESCRIPTION3'},
                                    $ref_line_short, \%hash_short);
  if ($ref_line_long)
  {
    &trans_display_description_table ('longdesc', 
                                      $text{'MODULE_CONFIG_LONG_DESCRIPTION3'},
                                      $ref_line_long, \%hash_long);
  }

  print qq(<div><button type="submit" name="update" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-check-circle-o"></i> <span>$text{'MODULE_CONFIG_UPDATE_BUTTON'}</span></button></div>);
}

print qq(</form>);
print qq(</p>);

&trans_footer ('', $text{'MODULE_INDEX'}, $_success, $_error, $_info);
