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
my $path = &trans_get_path ('', '') . "/$app";
my $monitor = $in{'monitor'};
my $finfo = (&trans_is_theme ($app)) ? 'theme' : 'module';

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
  # updated translation
  elsif ($in{'o'} eq 'update_trans')
  {
    $ret = 
      sprintf qq(<p><b>$text{'MSG_UPDATED_TRANSLATION'}</b></p>), $in{'t'};
  }
  
  return $ret;
}

sub trans_display_description_table ( $ $ $ \@ )
{
  my ($type, $title, $ref_line, $h) = @_;
  my %hash = %$h;

  print qq(<p><table>);
  print qq(<tr><td>&nbsp;</td></tr>);
  print qq(<tr><td $tb><b>$title</b></td></tr>);
  print qq(<tr><td $cb><code>$ref_line</code></td></tr>);
  print qq(</table>);

   print qq(<p><table>);
  print qq(<tr><td colspan="2">&nbsp;</td></tr>);
  print qq(<tr><td $tb><b>$text{'LANGUAGE'}</b></td><td $tb><b>$text{'DESCRIPTION'}</b></td></tr>);
  foreach my $key (sort keys %hash)
  {
    next if (!&trans_is_language ($key));
    my $value_print = &html_escape ($hash{$key});
    my $b1 = '';
    my $b2 = '';
    
    ($b1, $b2) = ('<b>', '</b>') if ($key eq $ref_lang);
    print qq(
      <tr>
      <td $cb>&nbsp;&nbsp;$b1$key$b2</td>
      <td><input type="text" value="$value_print" name="${type}_$key" size="80"></td></tr>);
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
# update module.info/theme descriptions
if ($in{'update'} ne '')
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
}
#
########################

&header(sprintf ($text{'FORM_TITLE'}, ($config{'trans_webmin'}) ? $text{'FORM_TITLE_W'} : $text{'FORM_TITLE_U'}), undef, "module", 1, 0, 0, qq(<b><a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a></b>));
&trans_translate_console_get_javascript ();
print "<hr>\n";
printf qq(<h1>$text{'MODULE_INFO_TITLE'}</h1>), $app;
&trans_get_menu_icons_panel ('module_info_main', $app);
print qq(<p>$text{'MODULE_INFO_DESCRIPTION'}</p>);

print qq(<p>);
print qq(<form action="module_info_main.cgi" method="post">);
print qq(<input type="hidden" name="old_app" value="$app">);
print qq(<input type="hidden" name="radio_select" value="">);
print qq(<select name="app" onChange="submit()">);
printf qq(<option value="">$text{'SELECT_MODULE'}</option>\n);
&trans_modules_list_get_options ([$app], '');
print "</select>";

&trans_monitor_panel ($app) if ($app ne '');

# display state message
print &my_get_msg ();

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

  print qq(<p><input type="submit" name="update" value="$text{'MODULE_CONFIG_UPDATE_BUTTON'}"></p>);
}

print qq(</form>);
print qq(</p>);

print qq(<hr>);
&footer("", $text{'MODULE_INDEX'});
