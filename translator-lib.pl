# Copyright (C) 2004-2012
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

use utf8;

do '../web-lib.pl';
&init_config();

# to translate usermin
&foreign_require ("usermin", "usermin-lib.pl");
# to use mailboxes settings
if ($config{'trans_use_mailboxes'})
{
  &foreign_require("mailboxes", "mailboxes-lib.pl");
}

%config_usermin = ();
&usermin::get_usermin_miniserv_config(\%config_usermin);

# global array for bad perl modules
# dependencies
my @perl_deps = ();

eval "use File::Path qw(make_path)";
push @perl_deps, 'File::Path' if ($@ ne '');
eval "use File::Copy";
push @perl_deps, 'File::Copy' if ($@ ne '');
eval "use Encode";
push @perl_deps, 'Encode' if ($@ ne '');
eval "use JSON";
push @perl_deps, 'JSON' if ($@ ne '');
eval "use HTML::Entities";
push @perl_deps, 'HTML::Entities' if ($@ ne '');
eval "use POSIX";
push @perl_deps, 'POSIX' if ($@ ne '');
eval "use File::Basename";
push @perl_deps, 'File::Basename' if ($@ ne '');
eval "use Digest::MD5 qw(md5_hex)";
push @perl_deps, 'Digest::MD5' if ($@ ne '');
eval "use Date::Manip";
push @perl_deps, 'Date::Manip' if ($@ ne '');
eval "use MIME::Lite";
push @perl_deps, 'MIME::Lite' if ($@ ne '');
if (!$config{'trans_use_mailboxes'})
{
  eval "use Mail::Sender";
  push @perl_deps, 'Mail::Sender' if ($@ ne '');
  
  # if CRAM-MD5 smtp auth method
  if ($config{trans_smtp_method} eq 'CRAM-MD5')
  {
    eval "use Digest::HMAC_MD5";
    push @perl_deps, 'Digest::HMAC_MD5' if ($@ ne '');
  }
  
  # if NTLM smtp auth method
  elsif ($config{trans_smtp_method} eq 'NTLM')
  {
    eval "use Authen::NTLM";
    push @perl_deps, 'Authen::NTLM' if ($@ ne '');
  }
}
# all binaries paths are here
my $all_path = (); &trans_init_all_path ();

&ReadParse();

our $ref_lang = &trans_get_ref_lang ($in{'app'});

# trans_get_ref_lang ()
# IN: -
# OUT: -
#
# init the global var for current ref language
#
sub trans_get_ref_lang ( $ )
{
  my $app = shift || '';

  return (
      $app &&
      $current_lang =~ /\.(.+)$/ &&
      -s &trans_get_path ($app, "lang/en.$1")
    ) ? "en.$1" : 'en';
}

# clean config inputs
&trans_trim_config ();

# trans_check_config ()
# IN: -
# OUT: -
#
# check if the module config is ok. if not, display a warning
# and exit
#
sub trans_main_check_config ()
{
  my $ok = 0;
  my $msg = '';

  if ($config{'trans_webmin'} != 1 && not %config_usermin)
  {
    $msg = $text{'MSG_ERROR_USERMIN'};
  }
  elsif ($config{'trans_working_path'} eq '' || ! -d $config{'trans_working_path'})
  {
    $msg = $text{'MSG_ERROR_WORKING_PATH'}
  }
  elsif ($config{'trans_email'} eq '')
  {
    $msg = $text{'MSG_ERROR_EMAIL'};
  }
  elsif (!$config{'trans_use_mailboxes'} && $config{'trans_smtp'} eq '')
  {
    $msg = $text{'MSG_ERROR_SMTP'};
  }
  else
  {
    $ok = 1
  }

  # if there was a problem, exit displaying
  # a message
  &trans_check_config_exit ($msg) if (not $ok);

  # create config directory for the current user
  make_path (
    "/$config{'trans_working_path'}/.translator/$remote_user/archives",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/usermin",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/webmin",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/usermin/ref",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/usermin/fingerprints",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/webmin/ref",
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/webmin/fingerprints",
    {
      'chmod' => 0700
    }
  );

  # modify permissions
  chmod (0700, "/$config{'trans_working_path'}/.translator");
}

# trans_trim_config ()
# IN: -
# OUT: -
#
# remove trailing and pending spaces from every module's
# config variable
#
sub trans_trim_config ()
{
 foreach $key (keys %config)
  {
    $config{$key} =~ s/(^\s+|\s+$)//g;
  } 
}

# trans_check_config_exit ( $ )
# IN: Message to display
# OUT: -
#
# print a message and exit
#
sub trans_check_config_exit ( $ )
{
  my $msg = shift;

  print qq(<p>$msg</p>) if ($msg);
  print qq(<hr>);
  &footer("/", $text{'index'});

  exit (1);
}

# trans_get_language_reference ( $ @ % )
# IN: 1 if there is reference language, 
#     array of files properties,
#     reference on the files hash table
# OUT: -
#
# return the reference language
# -> arg 2 could be modified
# 
sub trans_get_language_reference ( $ @ % )
{
  my ($have_ref, @rows, $p1) = @_;
  my (%file_ref) = %$p1;

  return if ($have_ref == 1);

  foreach my $item (@rows)
  {
    my %row = %$item;
    
    if ($row{'language'} eq $ref_lang)
    {
      $row{'reference'} = 1;
      %$item = %row;
      %file_ref = \$row{'file'};
      
      return;
    }
  }
}

# trans_get_diff_removed ( $ $ % % )
# IN: reference language,
#     translation language,
#     reference on the reference file,
#     reference on the translation file
# OUT: number of items present in the translation
#      file and removed in the reference file
#
# return the number of removed items
# 
sub trans_get_diff_removed ( $ $ % % )
{
  my ($ref, $lang, $p1, $p2) = @_;
  my (%file_ref) = %$p1;
  my (%file) = %$p2;
  my $removed = 0;

  return 0 if ($ref eq $lang);

  foreach my $trans (keys %file)
  {
    my $found = 0;

    foreach my $ref (keys %file_ref)
    {
      if ($trans eq $ref)
      {
        $found = 1;
        last;
      }
    }

    ++$removed if (!$found && $ref ne '');
  }

  return $removed;
}

# trans_get_diff_new ( $ $ % % )
# IN: reference language,
#     translation language,
#     reference on the reference file,
#     reference on the translation file
# OUT: number of items present in reference file and 
#      not in the translation file
#
# return the number of new items
#
sub trans_get_diff_new ( $ $ % % )
{
  my ($ref, $lang, $p1, $p2) = @_;
  my (%file_ref) = %$p1;
  my (%file) = %$p2;
  my $new = 0;
  
  return 0 if ($ref eq $lang);
  
  foreach my $ref (keys (%file_ref))
  {
    my $found = 0;
    
    foreach my $trans (keys %file)
    {
      if ($trans eq $ref && $file{$trans} ne '')
      {
        $found = 1;
        last;
      }
    }

    ++$new if (!$found && $ref ne '');
  }

  return $new;
}

# trans_get_hash_diff_new ( $ $ % % )
# IN: reference language,
#     translation language,
#     reference on the reference file,
#     reference on the translation file
# OUT: hash table of items present in reference file and 
#      not in the translation file
#
# return a hash of the new items
#
sub trans_get_hash_diff_new ( $ $ % % )
{
  my ($ref, $lang, $p1, $p2) = @_;
  my (%file_ref) = %$p1;
  my (%file) = %$p2;
  my %new = ();

  return 0 if ($ref eq $lang);

  foreach my $ref (keys (%file_ref))
  {
    my $found = 0;
    
    foreach my $trans (keys %file)
    {
      if ($trans eq $ref && $file{$trans} ne '')
      {
        $found = 1;
        last;
      }
    }

    $new{$ref} = $file_ref{$ref} if (!$found && $ref ne '');
  }

  return %new;
}

# trans_get_hash_diff_removed ( $ $ % % )
# IN: reference language,
#     translation language,
#     reference on the reference file,
#     reference on the translation file
# OUT: hash table of items present in reference file and 
#      not in the translation file
#
# return a hash of the removed items
#
sub trans_get_hash_diff_removed ( $ $ % % )
{
  my ($ref, $lang, $p1, $p2) = @_;
  my (%file_ref) = %$p1;
  my (%file) = %$p2;
  my %removed = ();

  return 0 if ($ref eq $lang);
  
  foreach my $trans (keys (%file))
  {
    my $found = 0;

    foreach my $ref (keys (%file_ref))
    {
      if ($trans eq $ref)
      {
        $found = 1;
        last;
      }
    }

    $removed{$trans} = $file{$trans} if (!$found && $trans ne '');
  }

  return %removed;
}

# trans_get_items ( $ )
# IN: path to the translation file
# OUT: a hash of key/value from the given translation file
#
# return a hash of key/value
# 
sub trans_get_items ( $ )
{
  my $path = shift;
  my %file = ();

  &trans_char2ent ($path, 'work');

  open (H, '<', $path);
  foreach my $line (<H>)
  {
    next if 
      $line =~ /^#/ or 
      $line =~ /^\s+#/;
    
    if ($line =~ /=/)
    {
      my ($name, $value) = split (/=/, $line, 2);
      $name =~ s/(^\s+|\s+$)//g;
      $value =~ s/(^\s+|\s+$)//g;

      next if $name eq '' or $value eq '';

      $file{"$name"} = $value;
    }
    elsif ($name ne '')
    {
      $file{"$name"} .= $line;
    }
  }
  close (H);

  &trans_char2ent ($path, 'html');
  
  return %file;
}

# trans_get_items_static ( $ )
# IN: path to the translation file
# OUT: a array of hash key/value from the given translation file
#
# same as trans_get_items() function, but return a array instead of a hash,
# to enable caller to keep the same order as in the origin file.
# each item of the array is a hash with key/value. the array order is the
# same as the file's lines order.
#
sub trans_get_items_static ( $ )
{
  my $path = shift;
  my $basen = basename ($path);
  my @file = ();
  my $count = 0;

  &trans_char2ent ($path, 'work');
  
  open (H, '<', $path);
  foreach my $line (<H>)
  {
    next if 
      $line =~ /^#/ ||
      $line =~ /^\s+#/;
      
    if ($line =~ /=/)
    {
      my %item = ();
      my ($name, $value) = split (/=/, $line, 2);
      $name =~ s/(^\s+|\s+$)//g;
      $value =~ s/(^\s+|\s+$)//g;

      next if ($name eq '' || $value eq '');

      $item{"$name"} = $value;
      $file[$count++] = \%item;
    }
# FIXME malformed item
#    elsif ($name ne '')
#    {
#      $item{"$name"} .= $line;
#    }
  }
  close (H);

  &trans_char2ent ($path, 'html');
  
  return @file;
}

# trans_get_string_from_size ( $ )
# IN: a size
# OUT: the same size, but with unit
#
# return a string with the size within
# 
sub trans_get_string_from_size ( $ )
{
  my $size = shift;
  my $ret = '';

  if ($size < 1024)
  {
    $ret = "$size bytes";
  }
  elsif ($size < 1024 * 1024)
  {
    $ret = sprintf "%.2f KB", $size / 1024, $size;
  }
  else
  {
    $ret = sprintf "%.2f MB", $size / (1024 * 1024), $size;
  }

  return $ret
}

# trans_build_cache ($ $ $ $ $ )
# IN: type ('interface' or 'config')
#     language
#     path to the file to cache
#     module's name
#     if we must take the root lang directory of webmin
# OUT: -
#
# build a cache file with md5 sums of each value.
# 
sub trans_build_cache ( $ $ $ $ $ )
{
  my ($type, $lang, $path, $app, $basic) = @_;
  my %hash = ();
  my $wu = &trans_get_current_app ();

  open (FD, '>', 
    "/$config{'trans_working_path'}/.translator/".
    "$remote_user/monitoring/$wu/fingerprints/${app}".(($basic)?'_lang':'').
    "-${type}_${lang}");
  %hash = &trans_get_items ($path);
  foreach my $key (keys %hash)
  {
    print FD "$key=" . (&md5_hex ($hash{$key})) . "|#|$hash{$key}\n";
  }
  close (FD);
}

# trans_get_updated ( $ $ $ $ )
# IN: type ('interface' or 'config')
#     language
#     module's name
#     use root webmin 'lang/' directory or not
# OUT: number of modified items in the reference language
# 
# return the number of modified items
# 
sub trans_get_updated ( $ $ $ $ )
{
  my ($type, $lang, $app, $basic) = @_;
  my $updated = 0;
  my %hash_lang = ();
  my $hash_md5 = ();
  my $path_lang = '';
  my $wu = &trans_get_current_app ();
  my $path_md5 = 
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/" .
    "fingerprints/${app}" . (($basic) ? '_lang' : '') . "-${type}_${lang}";

  return 0 if (! -f $path_md5);

  if ($type eq 'interface')
  {
    $path_lang = ($basic) ?
      "$root_directory/lang/$lang" : &trans_get_path ($app, "lang/$lang");
  }
  else
  {
    $path_lang = &trans_get_path ($app, "config.info.$ref");
    $path_lang = &trans_get_path ($app, 'config.info') if (! -f $path_lang);
  }

  %hash_lang = &trans_get_items ($path_lang);
  %hash_md5 = &trans_get_items ($path_md5);
  foreach my $key (keys %hash_md5)
  {
    my $md5_old = '';
    my $md5_new = '';

    next if ($hash_lang{$key} eq '');
    
    $md5_new = &md5_hex ($hash_lang{$key});
    $md5_old = (split (/\|#\|/, $hash_md5{$key}))[0];
    $updated++ if ($md5_new ne $md5_old);
  }

  return $updated;
}

# 
# trans_get_array_updated ( $ $ $ )
# IN: type ('interface' or 'config')
#     language
#     module's name
# OUT: array with hash of modified items in the reference language
# 
# same as trans_get_updated() function, but return a array instead of a hash.
# each item of the array is a hash with:
# 	key (translation key)
# 	old (old value)
# 	new (new value)
#
sub trans_get_array_updated ( $ $ $ )
{
  my ($type, $lang, $app) = @_;
  my @updated = ();
  my %hash_lang = ();
  my $hash_md5 = ();
  my $path_lang = '';
  my $wu = &trans_get_current_app ();
  my $path_md5 = 
    "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/fingerprints/${app}-${type}_${lang}";

  return 0 if (! -f $path_md5);

  if ($type eq 'interface')
  {
    $path_lang = &trans_get_path ($app,"lang/$lang");
  }
  else
  {
    $path_lang = &trans_get_path ($app, "config.info.$ref");
    $path_lang = &trans_get_path ($app, 'config.info') if (! -f $path_lang);
  }

  %hash_lang = &trans_get_items ($path_lang);
  %hash_md5 = &trans_get_items ($path_md5);
  foreach my $key (keys %hash_md5)
  {
    my $md5_old = '';
    my $md5_new = '';
    my $string_old = '';

    next if ($hash_lang{$key} eq '');
    
    $md5_new = &md5_hex ($hash_lang{$key});
    ($md5_old, $string_old) = (split (/\|#\|/, $hash_md5{$key}))[0,1];
    
    if ($md5_new ne $md5_old)
    {
      my %hash = ();

      %hash = (
        'key' => $key,
	'old' => $string_old,
	'new' => $hash_lang{$key}
      );
      push @updated, \%hash;
    }
  }

  return @updated;
}

# trans_get_item_updated ( \@ $)
# IN: array of hash
#     key
# OUT: a hash with key, old and new value
#
# return a hash corresponding to the given key
# 
sub trans_get_item_updated ( \@ $)
{
  my ($array, $item) = @_;
  
  foreach my $h (@$array)
  {
    my %hash = %$h;

    return %hash if ($hash{'key'} eq $item);
  }
}

# trans_get_unused ( $ $ $ )
# IN: type ('interface' or 'config')
#     language
#     module's name
# OUT: a hash with unused items
# 
# return a hash table with items in the reference translation file that are not
# used in the module files
# 
sub trans_get_unused ( $ $ $ )
{
  my ($type, $lang, $app) = @_;
  my %unused = ();
  my %hash = ();
  my $path_lang = '';
  my $path_search = '';
  my $grep_string = ''; 

  if ($type eq 'interface')
  {
    $path_lang = &trans_get_path ($app, "lang/$lang");
  }
  else
  {
    $path_lang = &trans_get_path ($app, "config.info.$lang");
    $path_lang = &trans_get_path ($app, "config.info") if (! -f $path_lang);
  }
    
  $path_search = (&trans_get_path ()) . "/$app/";
  $grep_string = "$path_search/* -r";

  %hash = &trans_get_items ($path_lang);
  foreach $key (keys %hash)
  {
    next if ($type eq 'config' and $key =~ /^line[0-9]*/);
    my @array = split (/\n/, `$all_path{'grep'} "$key" $grep_string`);

    if (not grep (/[\'|\"]$key[\'|\"]/, @array))
    {
      $unused{$key} = $hash{$key};

      if ($type eq 'interface')
      {
        delete $unused{$key}
          if (grep (/text\b.*[\(|\{][\'|\"]*$key[\'|\"]*/, @array));
      }
      else
      {
        delete $unused{$key}
          if (grep (/config\b.*\{[\'|\"]*$key[\'|\"]*\}/, @array));
      }
    }
  }

  return %unused;
}

# trans_get_existing_translations ( \@ )
# IN: module names in a array
# OUT: a array with translations name
#
# return a array with strings of translations for a given
# module
# 
sub trans_get_existing_translations ( \@ )
{
  my $a = shift;
  my @app = @$a;
  my @array = ();
  my %hash = ();

  # list all languages for all modules
  if (scalar (@app) == 0)
  {
    my @mlist = grep {&check_os_support($_)} &get_all_module_infos ();

    foreach my $m (@mlist)
    {
      my $dir = $m->{'dir'};
      
      opendir (DIR, &trans_get_path ($dir, 'lang/'));
      foreach my $item (readdir (DIR)) 
      {
        $hash{$item} = '' if &trans_is_language ($item, 1);
      }
      closedir (DIR);
    }
  }
  # just list all languages for a given module
  else
  {
    foreach my $mod (@app)
    {
      opendir (DIR, &trans_get_path ($mod, 'lang/'));
      foreach my $item (readdir (DIR)) 
      {
        $hash{$item} = '' if &trans_is_language ($item, 1);
      }
      closedir (DIR);
    }
  }

  delete $hash{$ref_lang};
  @array = keys %hash;

  return sort @array;
}

# get_languages_infos ( $ )
# IN: language
# OUT: language properties hashref + 'current_compat' key if the given language
#      is compatible with the current webmin/usermin language
#
# get infos for a given language
#
sub get_languages_infos ( $ )
{
  my $lang = shift;
  my @langs = &list_languages();
  my %data;
  my $ret;
  
  foreach my $l (@langs)
  {
    $data{$l->{'lang'}} = $l;
  }

  if (exists ($data{$lang}))
  {
    $ret = $data{$lang};
    $ret->{'current_compat'} = (
      $ret->{'charset'} eq $data{$current_lang}{'charset'}
    );
  
  }

  return $ret;
}

# trans_create_translation ( $ $ )
# IN: language
#     module's name
# OUT: 
# 	0: ok
# 	1: this language already exists
# 	2: bad input
#
# create all files and item for a new translation
# 
sub trans_create_translation ( $ $ )
{
  my ($lang, $app) = @_;
  my $path = (&trans_get_path ()) . "/$app";
  my @content = ();

  $lang =~ s/(^\s+|\s+$)//g;

  # bad
  return 2 if not &trans_is_language ($lang); 
  # already exist
  return 1
    if (grep /^$lang$/, &trans_get_existing_translations ([$app]));
 
  if ($config{'trans_webmin'} == 1)
  {
    # config.info
    if ((-f "$path/config.info") and (! -f "$path/config.info.$lang"))
    {
      open (H, '>', "$path/config.info.$lang") && close (H);
    }
    # lang
    if (! -f "$path/lang/$lang")
    {
      open (H, '>', "$path/lang/$lang") && close (H);
    }

    # lang - Webmin module exception (2 languages files)
    if ($path =~ m|/webmin$| && ! -f "$root_directory/lang/$lang") 
    {
      open (H, '>', "$root_directory/lang/$lang") && close (H)
    }
  }
  else
  {
    # config.info
    if (-f "$path/uconfig.info" && ! -f "$path/uconfig.info.$lang")
    {
      open (H, '>', "$path/uconfig.info.$lang") && close (H);
    }
    # lang
    make_path ("$path/ulang", {'chmod' => 700});
    if (! -f "$path/ulang/$lang")
    {
      open (H, '>',"$path/ulang/$lang") && close (H);
    }
  }
  
  # theme.info (for theme)
  if (&trans_is_theme ($app))
  {
    open (H, '<', "$path/theme.info");
    @content = <H>;
    close (H);

    if (!grep /^desc_$lang=/, @content)
    {
      open (H, '>>', "$path/theme.info");
      print H "desc_$lang=\n";
      close (H);
    }
  }
  # module.info
  elsif (! -f "$path/module.info.$lang")
  {
    open (H, '>', "$path/module.info.$lang");
    print H "desc_$lang=\n";
    close (H);
  }
  
  return 0;
}

# trans_is_theme ( $ )
# IN: module/theme name
# OUT: 
# 	0: is a module
# 	1: is a theme
#
# check if a given module is a theme
#
sub trans_is_theme ( $ )
{
  my $app = shift;
  my $path = &trans_get_path ($app, 'theme.info');

  return (-f $path);
}

# trans_is_language ( $ $ )
# IN: language, 1 to not check for specific encoding
# OUT: 
# 	0: not valid
# 	1: valid
#
# check if a given language code is valid
# 
sub trans_is_language ( $ $ )
{
  my ($lang, $nocheck) = @_;
  my $len = length ($lang);
  
  return 0 if (!$nocheck && $lang ne $ref_lang &&
    (
      $current_lang =~ /\.(.+)$/ && $lang !~ /\.$1$/ ||
      $lang =~ /\.(.+)$/ && $current_lang !~ /\.$1$/
    )
  );
  
  # FIXME
  # bad bad check... must be optimized!
  return !( 
    $len < 2 ||
    ($len > 2 && $lang !~ /[_\-\.]/) ||
    ($len > 5 && $lang !~ /\./) ||
    $lang =~ /^\./ ||
    $lang eq 'si' ||
    $lang =~ /[\*,\|<>\{\}]/
  );
}

# trans_footer ()
# IN: -
# OUT: -
#
# display the version of this module
# 
sub trans_footer ()
{
  my $wbmtranslator_version = $module_info{'version'};

  print qq(<p><i>wbmtranslator</i> <b>$wbmtranslator_version</b></p>);
}

# trans_archive_create ( $ $ \@ )
# IN: file name
#     language ('' for all languages)
#     modules names in a array
# OUT: -
#
# create a archive for a given or multiple modules translations
# 
sub trans_archive_create ( $ $ \@)
{
  my ($filename, $lang, $array) = @_;
  my @app = @$array;
  my $path = '';
  my $path_lang = '';
  my $path_module = '';
  my $path_help = '';
  my $path_config = '';
  my $root = &trans_get_path ();

  foreach my $mod (@app)
  {
    $path = $root;
    $tmp_path_lang = '';
    $tmp_path_module = '';
    $tmp_path_help = '';
    $tmp_path_config = '';
    
    $path = ($mod ne '') ? "$mod" : '*';
  
    # lang
    if (-d "$root/$path/lang")
    {
      $tmp_path_lang .= " $path/lang";
      $tmp_path_lang .= ($lang ne '') ? "/$lang" : '/';
    }

    # Webmin module exception (2 languages files)
    if ($path eq 'webmin' && -d "$root/lang")
    {
      $tmp_path_lang .= " lang";
      $tmp_path_lang .= ($lang ne '') ? "/$lang" : '/';
    }

    # ulang
    if (-d "$root/$path/ulang")
    {
      $tmp_path_lang .= " $path/ulang";
      $tmp_path_lang .= ($lang ne '') ? "/$lang" : '/';
    }

    # help
    if (-d "$root/$path/help")
    {
      $tmp_path_help .= "$path/help";
      $tmp_path_help .= ($lang ne '') ? "/*.$lang.*" : '/';
    }

    # module.info.*/theme.info.*
    if ($lang ne '')
    {
      $tmp_path_config .= " $path/module.info"
        if (-f "$root/$path/module.info");
      $tmp_path_config .= " $path/theme.info"
        if (-f "$root/$path/theme.info");
      $tmp_path_config .= " $path/module.info.$lang"
        if (-f "$root/$path/module.info.$lang");
      $tmp_path_config .= " $path/theme.info.$lang"
        if (-f "$root/$path/theme.info.$lang");
    }
    else
    {
      $tmp_path_config .= " $path/module.info*";
      $tmp_path_config .= " $path/theme.info*" if (-f "$path/theme.info");
    }

    # config.info/uconfig.info
    if ($lang ne '')
    {
      $tmp_path_config .= " $path/config.info.$lang"
        if (-f "$root/$path/config.info.$lang");
      $tmp_path_config .= " $path/uconfig.info.$lang"
        if (-f "$root/$path/uconfig.info.$lang");
    }
    else
    {
      $tmp_path_config .= " $path/config.info*";
      $tmp_path_config .= " $path/uconfig.info*" if (-f "$path/uconfig.info");
    }

    $path_lang .= " $tmp_path_lang";
    $path_module .= " $tmp_path_module";
    $path_help .= " $tmp_path_help";
    $path_config .= " $tmp_path_config";
  }

  system (
    "cd $root; $all_path{'tar'} --exclude=.* -zcf /$config{'trans_working_path'}/.translator/$remote_user/archives/$filename " .
    "$path_lang " .
    "$path_help " .
    "$path_module " .
    "$path_config"
  );
}

# trans_archive_send_browser ( $ )
# IN: file name
# OUT: -
#
# send a file to a browser in order to download it
# 
sub trans_archive_send_browser ( $ )
{
  my $file = shift;
  my $filename = $file;
  my $file = "/$config{'trans_working_path'}/.translator/$remote_user/archives/$file";
  my $size = (stat ($file))[7];
  my $date = strftime ("%a, %d %b %Y %H:%M:%S", localtime);
 
  print qq(Content-Type: application/tar+gzip\n);
  print qq(Content-Length: $size\n);
  print qq(Expires: $date GMT\n);

  if ($ENV{'HTTP_USER_AGENT'} =~ /MSIE/)
  {
    print qq(Content-Disposition: inline; filename="$filename"\n);
    print qq(Cache-Control: must-revalidate, post-check=0, pre-check=0\n);
    print qq(Pragma: public\n);
  }
  else
  {
    print qq(Content-Disposition: attachment; filename="$filename"\n);
    print qq(Pragma: no-cache\n);
  }

  print "\n";

  open (H, '<', $file);
  print <H>;
  close (H);
}

# trans_archive_delete ( $ )
# IN: filename
# OUT: -
#
# delete a wbmtranslator temporary file
# 
sub trans_archive_delete ( $ )
{
  my $filename = shift;

  unlink ("/$config{'trans_working_path'}/.translator/$remote_user/archives/$filename");
}

# trans_archive_list_content ( $ )
# IN: file name
# OUT: -
#
# display the content of the translation archive file
# 
sub trans_archive_list_content ( $ )
{
  my $filename = shift;

  open (H, "$all_path{'tar'} -ztf /$config{'trans_working_path'}/".
           ".translator/$remote_user/archives/$filename |");
  while (my $line = <H>)
  {
    my $color = 'green';
    
    if ($line =~ /\/(lang|ulang|help)\//)
    {
      if ($line =~ /\/help\//)
        {$color = 'brown';}
      elsif ($line =~ /\/(lang|ulang)\//)
        {$color = 'orange';}

      $line =~ 
        s/^(.*)\/(.*)\/(.*)$/
	  <font color="blue">$1<\/font>\/
	  <font color="$color">$2<\/font>\/
	  <font color="green">$3<\/font>/g;
    }
    else
    {
      if ($line =~ /config\.info/)
        {$color = 'purple';}
      elsif ($line =~ /module\.info/)
        {$color = 'gray';}
	
      $line =~ 
        s/^(.*)\/(.*)$/
	  <font color="blue">$1<\/font>\/
	  <font color="$color">$2<\/font>/g;
    }
    print "$line<br>\n";
  }
  close (H);
}

# trans_has_command ( $ )
# IN: binary to test
# OUT: system path for this binary
# 
# Search and return path for a given binary file
# -> trans_init_all_path () need to be call before
#    this function
# 
sub trans_has_command
{
  my $exe = shift;
  my @path = (
    '/bin/',
    '/sbin/',
    '/usr/bin/',
    '/usr/sbin/',
    '/usr/local/bin/',
    '/usr/local/sbin/',
    '/opt/bin/',
    '/opt/sbin/',
    '/opt/local/bin/',
    '/opt/local/sbin'
  );
  
  foreach my $item (@path)
  {
    return $item if (-e $item . $exe);
  }

  return '';
}

# trans_init_all_path ()
# IN: -
# OUT: -
#
# Initialize binaries pathes
# 
sub trans_init_all_path
{
  my @exe = (
    'chmod',
    'grep',
    'mv',
    'tar'
  );
  
  foreach my $item (@exe)
    {$all_path{$item} = &trans_has_command ($item) . $item;}
}

# trans_archive_send ( $ $ $ $ $ \@ $ )
# IN: from
#     to
#     sender name
#     translator message
#     file name of the file to attach
#
#     languages in the archive
# OUT: 0 if error
#
# send a email with the translations archive in attachement
# 
sub trans_archive_send ( $ $ $ $ $ \@ $ )
{
  my ($from, $to, $sender_name, $body, $file, $array, $lang) = @_;
  my $webmin_version = &get_webmin_version ();
  my $usermin_version = &usermin::get_usermin_version ();
  my $version = ($config{'trans_webmin'}) ? $webmin_version : $usermin_version;
  my @app = @$array;
  my $filename = $file;
  my $subject = '';
  my $message = '';
  my $mods_list = '';
  my $ret = 0;
  my $m = undef;
  my $multiple_modules = (scalar (@app) > 1);
  my $mail = undef;
  my $mtype = ($config{'trans_webmin'}) ? 'Webmin' : 'Usermin';

  $body =~ s/(^\s+|\s+$)//g;
  
  foreach my $mod (@app) {$mods_list .= "$mod, "}
  $mods_list =~ s/\, $//g;
  
  $subject = sprintf (
    "[$mtype] Translations ($mods_list - %s)",
    ($lang eq '') ? 'All languages' : "$lang"
  );

  $message .= qq(Translator : $sender_name <$from>\n);
  $message .= sprintf qq(Module(s) : $mods_list\n);
  $message .= sprintf qq(Language(s) : %s\n), ($lang eq '') ? 'All' : $lang;
  $message .= qq(Archive name : $filename\n);
  $message .= sprintf qq(Module(s) type : %s\n),
    (&trans_is_webmin_module ($app[0])) ? 
      "Core $mtype module(s)" : "Not Core $mtype module(s)";
  $message .= qq($mtype version : $version\n\n);
  
  if ($body eq '')
  {
    $message .= qq(Hi,\n\n);
    $message .= qq(Please find some translation(s) for $mtype module(s).\n\n);
    $message .= qq(Have a nice day :-\));
  }
  else
  {
    $message .= qq(*Message from the translator*:\n\n$body);
  }

  $message .= qq(\n\n-- Automatically generated with wbmtranslator --\n\n);

  # do not use mailboxes settings
  if (!$config{'trans_use_mailboxes'})
  {
    # with auth
    if ($config{'trans_smtp_user'} && $config{'trans_smtp_pwd'})
    {
      $m = new Mail::Sender ({
        smtp => $config{'trans_smtp'},
        from => $from,
        auth => $config{trans_smtp_method},
        authid => $config{'trans_smtp_user'},
        authpwd => $config{'trans_smtp_pwd'},
        debug => "/$config{'trans_working_path'}/.translator/$remote_user/mail_sender_debug.txt"
      });
    }
    # without auth
    else
    {
      $m = new Mail::Sender ({
        smtp => $config{'trans_smtp'},
        from => $from,
        debug => "/$config{'trans_working_path'}/.translator/$remote_user/mail_sender_debug.txt"
      });
    }

    if ($Mail::Sender::Error)
    {
      return (0, $Mail::Sender::Error);
    }

    $m->MailFile ({
      to => $to,
      subject => $subject,
      msg => $message,
      file => "/$config{'trans_working_path'}/.translator/$remote_user/archives/$file"
    });
  
    if ($Mail::Sender::Error)
    {
      return (0, $Mail::Sender::Error);
    }
  }
  # use mailboxes settings
  else
  {
    my $mail = undef;
    my $attach = '';
    
    open (H, '<', "/$config{'trans_working_path'}/.translator/".
                  "$remote_user/archives/$file");
    foreach (<H>) {$attach .= $_}
    close (H);
    
    $mail = { 
      'headers' => [ 
        ['From', $from],
        ['To', $to],
	['Subject', $subject]
      ],
      'attach' => [{ 
        'headers' => [ 
	  ['Content-Type', 'text/plain'],
	  ['Content-description', 'Mail message body'],
	  ['Content-transfer-encoding', '7BIT'],
	  ['Content-disposition', 'inline']
        ], 
        'data' => $message 
      }, {
        'headers' => [
          ['Content-Type', "application/octet-stream; name=\"$file\"; " .
	                   'type=Unknown;'],
	  ['Content-description', $file],
	  ['Content-transfer-encoding', 'Base64'],
	  ['Content-disposition', "attachment; filename=\"$file\""]
	],
	'data' => $attach
      }]
    };
    
    return 0 if (!&mailboxes::send_mail ($mail));
  }
  
  return (1, '');
}

# trans_check_config_exit ( $ )
# IN: Message to display
# OUT: -
#
# print a message and exit
#
sub trans_check_config_exit ( $ )
{
  my $msg = shift;
  
  print qq(<p>$msg</p>) if ($msg);
  print qq(<hr>);
  &footer("/", $text{'index'});
  
  exit (1);
}

# trans_send_check_config ()
# IN: -
# OUT: -
#
# check if config is ok for sending a email
# 
sub trans_send_check_config ()
{
  &trans_check_config_exit ($text{'MSG_CONFIG_SMTP_EMAIL'}) 
    if (
      (!$config{'trans_use_mailboxes'} && !$config{'trans_smtp'}) or
      (!$config{'trans_email'})
    );
}

# trans_email_check ( $ )
# IN: email
# OUT: 0 if bad
#
# check a email format
# 
sub trans_email_check ( $ )
{
  my $email = shift;

  return ($email =~ /[ |\t|\r|\n]*\"?([^\"]+\"?@[^ <>\t]+\.[^ <>\t][^ <>\t]+)[ |\t|\r|\n]*/) ? $1 : '';
}

# trans_char2ent ( $ $ )
# IN: file name (with full path)
#     type ('work' to decode and 'html' to encode)
# OUT: -
#
# Encode or decode entities in file
# 
sub trans_char2ent ( $ $ )
{
  my ($path, $type) = @_;
  my $reg = &trans_get_path ('', '') . '/lang';
  my $lang = '';

  $path =~ s/\/\//\//g;

  # FIXME
  # do not work with webmin "/lang/*" files
  return if ($path =~ /$reg/);

  # fingerprint file (always in en/en.UTF-8 language)
  if ($path =~ /fingerprints/)
  {
    $lang = $ref_lang;
  }
  # config.info file
  elsif ($path =~ /config\.info/)
  {
    $lang = ($path =~ /config\.info\.(.*)/) ? $1 : $ref_lang;
  }
  # main translation file
  else
  {
    $path =~ /\/(lang|ulang)\/(.*)/; $lang = $2;
  }

  return if (!&trans_lang_must_be_encoded ($lang));

  open (my $fh, '<', $path);
  read ($fh, my $src, -s $fh);
  close ($fh);

  my $dest = ($type eq 'work') ?
               &trans_ent2char_buffer ($src) :
               &trans_char2ent_buffer ($src);

  open (H, '>', $path);
  print H $dest;
  close (H);
}

# trans_ent2char_buffer ( $ )
# IN: buffer to decode
# OUT: decoded buffer
# 
#TODO remove this method soon or later
sub trans_ent2char_buffer ( $ ) 
{
  my $line = shift;

  $line =~ s/&#(\d\d\d);/chr($1)/ge;

  return $line;
}

# trans_char2ent_buffer ( $ )
# IN: buffer to encode
# OUT: encoded buffer
#
sub trans_char2ent_buffer ( $ )
{
  my $line = shift;
#FIXME
return $line;

  $line =~ s/(.)/(ord $1 > 127) ? '&#'.ord($1).';' : $1/ge;

  return $line;
}

# trans_get_module_version ( $ )
# IN: module name
# OUT: version
#
# return the version for a given module
# 
sub trans_get_module_version ( $ )
{
  my $app = shift;
  my $ret = '';
  my $finfo = (&trans_is_theme ($app)) ? 'theme' : 'module';

  return '' if ($app eq '');

  open (H, '<', &trans_get_path ($app, "$finfo.info"));
  while (<H>)
  {
    my ($name, $value) = split (/=/);
    
    if ($name eq 'version')
    {
      $value =~ s/\s+//g;
      $ret = $value;
      last;
    }
  }
  close (H);

  return $ret;
}

# trans_check_perl_deps ()
# IN: -
# OUT: -
#
# check if all dependencies are ok for perl
# -> test them before with the "eval" function and push all bad
#    dependencies in the global @perl_deps array
# 
sub trans_check_perl_deps ()
{
  return if (!scalar (@perl_deps)); 
    
  print qq($text{'PERL_DEPS_ERROR'});
  print qq(<ul>);
  foreach my $mod (@perl_deps) {print qq(<li><b>$mod</b></li>\n);}
  print qq(</ul><hr>);
}

# trans_get_translation_filename ( \@ $ )
# IN: array of modules name
#     language ('' for all)
# OUT: -
#
# build the file name for the translations archive
# 
sub trans_get_translation_filename ( \@ $ )
{
  my ($array, $lang) = @_;
  my @app = @$array;
  my $date = strftime ("%Y%m%d", localtime);
  my $webmin_version = &get_webmin_version ();
  my $usermin_version = &usermin::get_usermin_version ();
  my $suffix = '';

  # if there is too many modules, do not display 
  # them all
  if (scalar (@app) < 2)
  {
    my $module_version = &trans_get_module_version ($app[0]);
    
    $suffix .= ($config{'trans_webmin'} == 1) ?
      ($module_version eq $webmin_version) ?
        $app[0] . '_' : $app[0] . "-${module_version}_" :
      ($module_version eq $usermin_version) ?
        $app[0] . '_' : $app[0] . "-${module_version}_";
  }
  else
  {
    $suffix .= "multiple_";
  }

  $suffix =~ s/\_$/-/;
  $suffix = ($config{'trans_webmin'} == 1) ?
    "webmin-${webmin_version}-$suffix" : 
    "usermin-${usermin_version}-$suffix";
  
  $lang = 'all' if ($lang eq '');
  $filename = "${suffix}$date-$lang.tar.gz";

  return $filename;
}

# trans_translate_console_get_javascript ( $ )
# IN: Translate to language
# OUT: -
#
# print the necessary javascript code to open the Bing console
# 
sub trans_translate_console_get_javascript ( $ )
{
  my $lang2 = shift;

  $lang2 =~ s/^([a-z]+).*/$1/i;

  print qq(
    <script language="javascript">
    function translate_console_open ()
    {
      window.open(
        'translate_popup.cgi?lang2=$lang2',
	'translate_popup',
	'toolbar=no,location=no,directories=no,status=no,scrollbars=yes,' +
	'resizable=no,copyhistory=no,width=600,height=400'
      );
    }
    </script>
  );
}

# trans_translate_console_display_link ()
# IN: -
# OUT: -
#
# print the javascript link to open the translation console popup
# 
sub trans_translate_console_display_link ()
{
  print qq(<a href="javascript:translate_console_open ();">$text{'TRANSLATE_CONSOLE_LINK'}</a>);
}

# trans_get_menu_icons_panel ( $ $ )
# IN: current section (interface_main, help_main, module_config_main, 
#                      module_info_main, send_main or admin_main)
#     current module
# OUT: -
#
# print a menu in a panel
# 
sub trans_get_menu_icons_panel ( $ $ )
{
  my $current = shift;
  my $app = shift || '';
  my (
       $interface, 
       $help, 
       $module_config, 
       $module_info,
       $send, 
       $admin
     ) = (
       ($current eq 'interface_main') ? 
         'interface_24x24_disable.png' : 'interface_24x24.png',
       ($current eq 'help_main') ? 
         'help_24x24_disable.png' : 'help_24x24.png',
       ($current eq 'module_config_main') ? 
         'module_config_24x24_disable.png' : 'module_config_24x24.png',
       ($current eq 'module_info_main') ? 
         'module_info_24x24_disable.png' : 'module_info_24x24.png',
       ($current eq 'send_main') ? 
         'send_24x24_disable.png' : 'send_24x24.png',
       ($current eq 'admin_main') ? 
         'admin_24x24_disable.png' : 'admin_24x24.png',
     );

  # interface translation
  print qq(<table border=0 cellspacing=1 cellpadding=1 bgcolor="silver"><tr>);
  print qq(<td><a href="interface_main.cgi?app=$app"><img border=0 src="images/$interface" alt="$text{'MENU_INTERFACE_MAIN_GO'}" title="$text{'MENU_INTERFACE_MAIN_GO'}"></a></td>);

  # help translation
  print qq(<td><a href="help_main.cgi?app=$app"><img border=0 src="images/$help" alt="$text{'MENU_HELP_MAIN_GO'}" title="$text{'MENU_HELP_MAIN_GO'}"></a></td>);
  
  # configuration translation
  print qq(<td><a href="module_config_main.cgi?app=$app"><img border=0 src="images/$module_config" alt="$text{'MENU_MODULE_CONFIG_MAIN_GO'}" title="$text{'MENU_MODULE_CONFIG_MAIN_GO'}"></a></td>);

  # module informations translation
  print qq(<td><a href="module_info_main.cgi?app=$app"><img border=0 src="images/$module_info" alt="$text{'MENU_MODULE_INFO_MAIN_GO'}" title="$text{'MENU_MODULE_INFO_MAIN_GO'}"></a></td>);

  # send
  print qq(<td><a href="send_main.cgi?app=$app"><img border=0 src="images/$send" alt="$text{'MENU_SEND_MAIN_GO'}" title="$text{'MENU_SEND_MAIN_GO'}"></a></td>);
  
  # administration translation
  print qq(<td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td><a href="admin_main.cgi?app=$app"><img border=0 src="images/$admin" alt="$text{'MENU_ADMIN_MAIN_GO'}" title="$text{'MENU_ADMIN_MAIN_GO'}"></a></td>);

  print qq(</tr></table>\n);
}

# trans_modules_list_get_options ( \@ $ )
# IN: array of items to select by default
#     type of the modules to display ('core', 'non-core', '')
# OUT: -
#
# display HTML options for a SELECT tag, with all
# modules ordered by name
# 
sub trans_modules_list_get_options ( \@ $ )
{
  my ($array, $module_type) = @_;
  my @app = @$array;
  my @mlist = sort { $a->{'dir'} cmp $b->{'dir'} }
    grep { &check_os_support($_) } &trans_get_all_module_infos ();
  
  foreach my $m (@mlist)
  {
    next if (
      ($module_type eq 'core' and not &trans_is_webmin_module ($m->{'dir'})) or
      ($module_type eq 'non-core' and &trans_is_webmin_module ($m->{'dir'}))
    );
    printf qq(<option value="%s"%s>%s : %s</option>\n),
      $m->{'dir'}, (grep /^$m->{'dir'}$/, @app) ? ' selected="selected"' : '', 
      $m->{'dir'}, $m->{'desc'};
  }
}

# trans_lang_must_be_encoded ( $ )
# IN: language to check
# OUT: 1 if it must be encoded/decoded
#
# check if a given language must be encode/decoded
# with char2ent.pl
# 
sub trans_lang_must_be_encoded ( $ )
{
  my $lang = shift;
  my @langs = &list_languages();

  foreach my $l (@langs)
  {
    if ($l->{'lang'} eq $lang)
    {
      return 1 if ($l->{'charset'} eq '' ||
                   $l->{'charset'} =~ /iso-8859-1/)
    }
  }

  return 0;
}

# trans_is_webmin_module ( $ )
# IN: module name
# OUT: 1 if it is a webmin module
#
# Check if a given application is a webmin module or
# not
# 
sub trans_is_webmin_module ( $ )
{
  my $module = shift;
  my @all_modules = &trans_init_all_core_modules ();

  return grep (/$module/, @all_modules); 
}

# trans_get_user_var_hash ( $ )
# IN: var name prefix ('monitor_', 'default_email_' etc.)
# OUT: var values
#
# return the values correponding to the given prefix name in a
# hash table (name=value)
#
sub trans_get_user_var_hash ( $ )
{
  my $name = shift;
  my %ret = ();

  open (H, '<', "/$config{'trans_working_path'}/.translator/".
                "$remote_user/user_vars") || return '';
  while (my $line = <H>) 
  {
    my ($n, $v) = split (/=/, $line);
    
    if ($n =~ /^$name(.*)$/)
    {
      $ret{$1} = $v;
    }
  }
  close (H);

  return %ret;
}

# trans_get_user_var ( $ )
# IN: var name
# OUT: var value
#
# return the value correponding to the given name
#
sub trans_get_user_var ( $ )
{
  my $name = shift;
  my $ret = '';

  open (H, '<', "/$config{'trans_working_path'}/.translator/".
                "$remote_user/user_vars") || return '';
  while ((my $line = <H>) && $ret eq '') 
  {
    my ($n, $v) = split (/=/, $line);
    $ret = $v if ($n eq $name);
  }
  close (H);

  return $ret;
}

# trans_set_user_var ( $ $ )
# IN: name
#     value
# OUT: -
#
# set a var in the user session file. Some more work is done if var concern
# monitoring (-> monitoring cache work is done)
#
sub trans_set_user_var ( $ $ )
{
  my ($name, $value) = @_;
  my %hash = ();
  my $reg = '^monitor_' . &trans_get_current_app () . '_(.*)$';
  my $wu = &trans_get_current_app ();
  
  # build cache for a given app if requested
  if ($name =~ /$reg/ && $value == 1)
  {
    &trans_build_cache ('interface', $ref_lang, &trans_get_path ($1, "lang/$ref_lang"), $1);
    &trans_build_cache ('config', $ref_lang, &trans_get_path ($1, 'config.info'), $1);
    copy (&trans_get_path ($1, "lang/$ref_lang"), "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/$1-interface_$ref_lang");
    copy (&trans_get_path ($1, 'config.info'), "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/$1-config_$ref_lang");

    if ($1 eq 'webmin')
    {
      &trans_build_cache ('interface', $ref_lang, "$root_directory/lang/$ref_lang", 'webmin_lang');
      copy ("$root_directory/lang/$ref_lang", "/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/webmin_lang-interface_$ref_lang");
    }
  }
  
  if (open (H, '<', "/$config{'trans_working_path'}/.translator/".
                    "$remote_user/user_vars"))
  {
    while (my $line = <H>) 
    {
      my ($n, $v) = split (/=/, $line);
      chomp ($v);
      $hash{$n} = $v;
    }
    close (H);
  }

  $hash{$name} = $value;

  open (H, '>', "/$config{'trans_working_path'}/.translator/".
                "$remote_user/user_vars");
  while (my ($k, $v) = each (%hash))
  {
    print H "$k=$v\n";
  }
  close (H);
}

# trans_monitor_panel ( $ )
# IN: module name
# OUT: -
#
# print a table with monitoring panel
#
sub trans_monitor_panel ( $ )
{
  my $app = shift;
  my $monitor = &trans_get_user_var ();
  
  $monitor = &trans_get_user_var ("monitor_" . &trans_get_current_app () . "_$app");
  $monitor = 0 if ($monitor eq '');
  
  printf qq(
    <p>
    <table style="background: silver;font-size: 10px;font-family: Verdana, Arial, Helvetica, sans-serif;color: black;border: 2px green solid;"><tr><td>
    $text{'MONITOR_MODULE'} 
    <input type="radio" id='m1' name="monitor" onChange="submit()" value="1"%s><label for='m1'>&nbsp;$text{'YES'}</label>
    <input type="radio" id='m2' name="monitor" onChange="submit()" value="0"%s><label for='m2'> $text{'NO'}</label>
    </td></tr></table>
    </p>
  ),
  ($monitor == 1) ? ' checked="checked"' : '',
  ($monitor == 0) ? ' checked="checked"' : '';
}

# trans_monitor_news ()
# IN: -
# OUT: -
#
# if there is update in monitored modules, print a table with
# those updates for each updated module
#
sub trans_monitor_news ()
{
  my %hash = &trans_get_user_var_hash ('monitor_'.&trans_get_current_app().'_');
  my $wu = &trans_get_current_app ();
  my $ret;

  foreach my $app (keys (%hash))
  {
    if ($hash{$app} == 1)
    {
      $ref_l = &trans_get_ref_lang ($app);

      my $changed = 0;
      my $item = '';
      my %file_ref = &trans_get_items (&trans_get_path ($app, "lang/$ref_l"));
      my %file = &trans_get_items ("/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/$app-interface_$ref_l");
      my $new = &trans_get_diff_new (' ', $ref_l, \%file_ref, \%file);
      my $removed = &trans_get_diff_removed (' ', $ref_l, \%file_ref, \%file);
      my $updated = &trans_get_updated ('interface', $ref_l, $app, '');
      
      if ($app eq 'webmin')
      {
        %file_ref = &trans_get_items ("$root_directory/lang/$ref_l");
        %file = &trans_get_items ("/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/webmin_lang-interface_$ref_l");

        $new = $new + &trans_get_diff_new (' ', $ref_l, \%file_ref, \%file);
        $removed = $removed + &trans_get_diff_removed (' ', $ref_l, \%file_ref, \%file);
        $updated = $updated + &trans_get_updated ('interface', $ref_l, 'webmin', '');
      }

      $item .= qq(<tr><td>$app</td>);
      if ($new > 0 or $removed > 0 or $updated > 0)
      {
        $changed = 1;

        $item .= qq(
	 <th><a href="/$module_name/interface_main.cgi?app=$app">$new</a></th>
	 <th><a href="/$module_name/interface_main.cgi?app=$app">$removed</a></th>
	 <th><a href="/$module_name/interface_main.cgi?app=$app">$updated</a></th>
	);
      }
      else
      {
        $item .= qq(<td colspan="3">&nbsp;</td>);
      }

      $new = $removed = $updated = 0;

      %file_ref = &trans_get_items (&trans_get_path ($app, 'config.info'));
      %file = &trans_get_items ("/$config{'trans_working_path'}/.translator/$remote_user/monitoring/$wu/ref/$app-config_$ref_l");

      $new = &trans_get_diff_new (' ', $ref_l, \%file_ref, \%file);
      $removed = &trans_get_diff_removed (' ', $ref_l, \%file_ref, \%file);
      $updated = &trans_get_updated ('config', $ref_l, $app, '');
      
      if ($new > 0 or $removed > 0 or $updated > 0)
      {
        $changed = 1;
        $item .= qq(
         <th><a href="/$module_name/module_config_main.cgi?app=$app">$new</a></th>
         <th><a href="/$module_name/module_config_main.cgi?app=$app">$removed</a></th>
         <th><a href="/$module_name/module_config_main.cgi?app=$app">$updated</a></th>
       );
      }
      else
      {
        $item .= qq(<td colspan="3">&nbsp;</td>);
      }
      
      $item .= qq(<td align=center><a href="index.cgi?remove=$app"><img title="$text{'REMOVE_FROM_MONITOR'}" border=0 src="/$module_name/images/delete.png"></a></td></tr>\n);

      $ret .= $item if ($changed == 1);
    }
  }

  if ($ret)
  {
    $ret = qq(
      <tr $tb><th>$text{'MODULE'}</th><th colspan="3">$text{'WEB_INTERFACE'}</th><th colspan="3">$text{'CONFIGURATION'}</th><th>$text{'ACTION'}</th></tr>
      <tr $tb><td>&nbsp;</td><td>$text{'ADDED'}</td><td>$text{'REMOVED'}</td><td>$text{'UPDATED'}</td>
      <td>$text{'ADDED'}</td><td>$text{'REMOVED'}</td><td>$text{'UPDATED'}</td><td>&nbsp;</td></tr>
      $ret
    );
  }
  else
  {
    $ret = '';
  }

  return $ret;
}

# trans_get_all_module_infos ()
# IN: -
# OUT: a array with modules information
#
# return a array with modules and themes informations
#
sub trans_get_all_module_infos ()
{
  return ($config{'trans_webmin'} == 1) ?
    (&webmin::list_themes (), &get_all_module_infos ()) :
    (&usermin::list_themes (), &usermin::list_modules ());
}

# trans_get_path ( $ $ $ )
# IN: current module
#     filename
#     if we must include or not module name in path
# OUT: a full path for the given file
#
# return a full path for a given file
#
sub trans_get_path ( $ $ $ )
{
  my ($app, $file, $basic) = @_;
  my $path = '';
  
  if ($app eq '' and $file eq '')
  {
    $path = ($config{'trans_webmin'} == 1) ?
      $root_directory : $config_usermin{'root'};
  }
  else
  {
    if ($config{'trans_webmin'} == 1)
    {
      $path = ($basic) ? "$root_directory/$file": "$root_directory/$app/$file";
    }
    else
    {
      if ($file =~ /^help/ or $file eq 'module.info' or $file eq 'theme.info')
      {
        $path = "$config_usermin{'root'}/$app/$file";
      }
      else
      {
        $path = (-e "$config_usermin{'root'}/$app/u$file") ?
	  "$config_usermin{'root'}/$app/u$file" :
          "$config_usermin{'root'}/$app/$file";
      }
    }
  }

  return $path;
}

# trans_get_current_app ()
# IN: -
# OUT: current app (webmin or usermin)
#
# return the current app selected by the user in the module's configuration
#
sub trans_get_current_app ()
{
  return ($config{'trans_webmin'} == 1) ? 'webmin' : 'usermin';
}

# trans_init_all_core_modules ()
# IN: -
# OUT: a array with core modules list
#
# return a array with webmin or usermin core modules/themes informations
#
sub trans_init_all_core_modules ()
{
  my @all_modules = ();
  my $type = ($config{'trans_webmin'} != 1) ? 'usermin' : 'webmin';
  
  open (H, '<', "data/$type-core-modules.data");
  while (<H>)
  {
    push @all_modules, $_;
  }
  close (H);

  return @all_modules;
}

# trans_init_translate_popup_langs ( $ )
# IN: Default translate to la,nguage.
# OUT: -
#
# retrieve translation user choice from the translation console from a cookie.
#
sub trans_init_translate_popup_langs ( $ $ )
{
  my $lang1 = $ref_lang;
  my $lang2 = shift || $current_lang;
  my @langs = values (%{$_[0]});

  ($lang1) = $lang1 =~ /^([a-z]+)/;
  ($lang2) = $lang2 =~ /^([a-z]+)/;

  $lang1 = $current_lang if (!grep (/^$lang1$/, @langs));
  $lang2 = $current_lang if (!grep (/^$lang2$/, @langs));

  return ($lang1, $lang2);
}

#################
#
sub trans_debug ( $ )
{
  use Data::Dumper;
  my $data = shift;
  open(H,'>>','/tmp/trans_debug.log');
  print H Dumper($data)."\n";
  close(H);
}
#
#################
1;
