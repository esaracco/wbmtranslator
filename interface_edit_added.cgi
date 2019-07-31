#!/usr/bin/perl

# Copyright (C) 2004-2019
# Emmanuel Saracco <emmanuel@esaracco.fr>
#
# GNU GENERAL PUBLIC LICENSE

require './translator-lib.pl';

my $app = $in{'app'};
my $lang = $in{'t'};
my $webmin_lang = $in{'webmin_lang'};
my %file = ($webmin_lang eq 'lang')  ?
  &trans_get_items ("$root_directory/lang/$lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$lang"));
my %file_ref = ($webmin_lang eq 'lang')  ?
  &trans_get_items ("$root_directory/lang/$ref_lang") :
  &trans_get_items (&trans_get_path ($app, "lang/$ref_lang"));
my %new = &trans_get_hash_diff_new ($ref_lang, $lang, \%file_ref, \%file);

##### POST actions #####
#
# add new items in the translation file
if (defined ($in{'update'}))
{
  my $updated = 0;
  my $url = "interface_main.cgi?app=$app&t=$lang&webmin_lang=$webmin_lang";
  
  foreach my $item (keys %in)
  {
    if ($item =~ /newitem_/)
    {
      $item =~ s/newitem_//g;
      if ($in{"newitem_$item"} ne '')
      {
        $updated = 1;
        $file{$item} = $in{"newitem_$item"};
      }
    }
  }

  if ($updated)
  {
    ($webmin_lang eq 'lang')  ?
      open (H, '>', "$root_directory/lang/$lang") :
      open (H, '>', &trans_get_path ($app, "lang/$lang"));
    foreach my $item (sort keys %file)
    {
      next if ($item eq '');
      print H "$item=$file{$item}\n";
    }
    close (H);
  
    # FIXME
    # do not encode webmin "/lang/*" files
    ($webmin_lang eq 'lang')  ?
      &trans_char2ent ("$root_directory/lang/$lang", 'work') :
      &trans_char2ent (&trans_get_path ($app, "lang/$lang"), 'html');

    $url .= '&o=add_new';
  }
  else
  {
    $url .= '&o=add_new_none';
  }
  
  &redirect ($url);
  exit;
}
#
########################

&trans_header ($text{'EDIT_ADDED_TITLE'}, $app, $lang);
printf (qq(<br/>$text{'EDIT_ADDED_DESCRIPTION'}), $ref_lang, $lang);

print qq(<p>);
print qq(<form action="interface_edit_added.cgi" method="post">);
print qq(<input type="hidden" name="app" value="$app">);
print qq(<input type="hidden" name="t" value="$lang">);
print qq(<input type="hidden" name="webmin_lang" value="$webmin_lang">);
print qq(<table class="trans keys-values" width="100%">);
foreach my $key (sort keys %new)
{
  printf (qq(
    <tr>
      <td>$key:</td>
      <td class="to-translate">%s</td>
    </tr>
    <tr>
      <td></td>
      <td><textarea name="newitem_$key" rows=5>$in{"newitem_$key"}</textarea></td>
    </tr>), &html_escape ($new{"$key"}));
}
print qq(</table>);
print qq(<p/><div><button type="submit" name="update" class="btn btn-success ui_form_end_submit"><i class="fa fa-fw fa-check-circle-o"></i> <span>$text{'UPDATE_TRANSLATION_FILE'}</span></button></div>);
print qq(</form>);
print qq(</p>);

&trans_footer ("interface_main.cgi?app=$app&webmin_lang=$webmin_lang", $text{'INTERFACE_INDEX'});
