#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my $target = $in{'c'};
my $webmin_lang = $in{'webmin_lang'};
my $finfo = (&trans_is_theme ($app)) ? 'theme' : 'module';
my $default_tab = $in{'tab'}||'';

##### POST action #####
#
# remove translation
if (defined ($in{'remove'}))
{
  # remove lang files
  if ($target eq 'all' || $target eq 'all_webmin' || $target eq 'lang')
  {
    unlink ("$root_directory/lang/$lang") if ($webmin_lang ne '');
    unlink ("$root_directory/$app/lang/$lang");
    # Webmin module exception (2 languages files)
    unlink ("$root_directory/lang/$lang") if ($app eq 'webmin');
  }

  # remove ulang files
  if ($target eq 'all' || $target eq 'all_usermin' || $target eq 'ulang')
  {
    unlink ("$config_usermin{'root'}/$app/ulang/$lang");
  }

  # remove config.info
  if ($target eq 'all' || $target eq 'all_webmin' || $target eq 'config_info')
  {
    unlink ("$root_directory/$app/config.info.$lang");
  }

  # remove uconfig.info
  if ($target eq 'all' || $target eq 'all_usermin' || $target eq 'uconfig_info')
  {
    unlink ("$config_usermin{'root'}/$app/uconfig.info.$lang");
  }

  # remove help files
  if ($target eq 'all' || $target eq 'all_webmin')
  {
    opendir (DIR, "$root_directory/$app/help/");
    while (my $file = readdir (DIR))
    {
      unlink ("$root_directory/$app/help/$file") if ($file =~ /\.$lang\./);
    }
    closedir (DIR);
  }

  # remove translation from webmin module.info/theme.info
  if ($target eq 'all' || $target eq 'all_webmin' || $target eq 'module_info')
  {
    unlink ("$root_directory/$app/$finfo.info.$lang");

    move ("$root_directory/$app/$finfo.info", "/$config{'trans_working_path'}/.translator/$remote_user/$app-$finfo.info$main::session_id");

    open (SRC, '<', "/$config{'trans_working_path'}/.translator/$remote_user/$app-$finfo.info$main::session_id");
    open (DST, '>', "$root_directory/$app/$finfo.info");
    foreach my $line (<SRC>)
    {
      next if $line =~ /desc_$lang/i;
      my ($name, $value) = split (/=/, $line, 2);
      print DST "$name=$value";
    }
    close (DST);
    close (SRC);
  }

  # remove translation from usermin module.info/theme.info
  if ($target eq 'all' || $target eq 'all_usermin' || $target eq 'umodule_info')
  {
    unlink ("$config_usermin{'root'}/$app/$finfo.info.$lang");

    move ("$config_usermin{'root'}/$app/$finfo.info",
      "/$config{'trans_working_path'}/.translator/$remote_user/$app-u$finfo.info$main::session_id");
    open (SRC, '<', "/$config{'trans_working_path'}/.translator/$remote_user/$app-u$finfo.info$main::session_id");
    open (DST, '>', "$config_usermin{'root'}/$app/$finfo.info");
    foreach my $line (<SRC>)
    {
      next if $line =~ /desc_$lang/i;
      my ($name, $value) = split (/=/, $line, 2);
      print DST "$name=$value";
    }
    close (DST);
    close (SRC);
  }

  &redirect ("$in{'referer'}.cgi?app=$app&t=$lang&o=remove_trans&webmin_lang=$webmin_lang&tab=$default_tab");
  exit;
}
#
########################

&trans_header ($text{'REMOVE_TRANSLATION_TITLE'}, $app, $lang);

print qq(<br/>);
if ($target eq 'all')
{
  ($webmin_lang ne '') ?
    printf ($text{'REMOVE_TRANSLATION_SPECIAL_DESCRIPTION'}, $lang, $lang, $lang) :
    printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_ALL'}, $lang, $lang, $lang, $lang, $app);
}
elsif ($target eq 'all_webmin')
{
  ($webmin_lang ne '') ?
    printf ($text{'REMOVE_TRANSLATION_SPECIAL_DESCRIPTION'}, $lang, $lang, $lang) :
    printf ($text{'REMOVE_TRANSLATION_DESCRIPTION'}, $lang, $lang, $lang, $app);
}
elsif ($target eq 'all_usermin')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_USERMIN'}, $lang, $lang, $lang, $app);
}
elsif ($target eq 'lang')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_LANG'}, $lang, $app);
}
elsif ($target eq 'ulang')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_ULANG'}, $lang, $app);
}
elsif ($target eq 'module_info')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_MODULE_INFO'}, $lang, $lang, $app);
}
elsif ($target eq 'config_info')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_CONFIG_INFO'}, $lang, $lang, $app);
}
elsif ($target eq 'umodule_info')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_UMODULE_INFO'}, $lang, $lang, $app);
}
elsif ($target eq 'uconfig_info')
{
  printf ($text{'REMOVE_TRANSLATION_DESCRIPTION_UCONFIG_INFO'}, $lang, $lang, $app);
}

print qq(<form action="remove.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app"/>);
print qq(<input type="hidden" name="tab" value="$default_tab"/>);
print qq(<input type="hidden" name="t" value="$lang"/>);
print qq(<input type="hidden" name="c" value="$target"/>);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang"/>);
print qq(<input type="hidden" name="referer" value="$in{'referer'}"/>);
print qq(<p/><div><button type="submit" name="remove" class="btn btn-danger"><i class="fa fa-fw fa-trash"></i> <span>$text{'REMOVE_TRANSLATION'}</span></button></div>);
print qq(</form>);

&trans_footer("$in{'referer'}.cgi?app=$app&webmin_lang=$webmin_lang&tab=$default_tab", $text{'PREVIOUS'});
